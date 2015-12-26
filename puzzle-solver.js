"use strict";

function PuzzleSolver(puzzle) {
  this.model = puzzle;
  this.pieces_by_id = {};

  for (var i in puzzle.pieces) {
    var id = puzzle.pieces[i].id;
    if (this.pieces_by_id[id] === undefined)
      this.pieces_by_id[id] = [];

    this.pieces_by_id[id].push(puzzle.pieces[i]);
  }

  this.piece_permutations = {};
  for (i in this.pieces_by_id) {
    this.piece_permutations[i] =
      PuzzleSolver.permutationsOf(this.pieces_by_id[i][0].final_positions);
  }
}

PuzzleSolver.permutationsOf = function (array) {
  if (array.length <= 1) return [array.slice()];
  var arrays = [];

  for (var i=0; i<array.length; ++i) {
    var rest = array.slice();
    var first = rest.splice(i,1);
    var sub = PuzzleSolver.permutationsOf(rest);
    for (var j=0; j<sub.length; ++j) {
      arrays.push(first.concat(sub[j]));
    }
  }
  return arrays;
};

PuzzleSolver.prototype.minHeuristic = function() {
  var min_moves = 0;
  for (var i=0; i<this.model.pieces.length; ++i) {
    var min_piece_dist = 0;
    var piece = this.model.pieces[i];
    for (var j=0; j<piece.final_positions.length; ++j) {
      var target = piece.final_positions[j];
      var dist = Math.abs(piece.position.x-target.x) +
        Math.abs(piece.position.y-target.y);
      if (j === 0 || dist < min_piece_dist)
        min_piece_dist = dist;
    }
    min_moves += min_piece_dist;
  }
  return min_moves;
};

PuzzleSolver.prototype.permutationHeuristic = function() {
  var min_moves = 0;

  for (var id in this.piece_permutations) {
    var min_piece_dists = 0;
    for (var p=0; p<this.piece_permutations[id].length; ++p) {
      var perm = this.piece_permutations[id][p];
      var perm_dist = 0;
      for (var j=0; j<perm.length; ++j) {
        var piece = this.pieces_by_id[id][j];
        var target = perm[j];
        perm_dist += Math.abs(piece.position.x-target.x) +
          Math.abs(piece.position.y-target.y);
      }
      if (p === 0 || perm_dist < min_piece_dists)
        min_piece_dists = perm_dist;
    }
    min_moves += min_piece_dists;
  }

  return min_moves;
};

PuzzleSolver.prototype.heuristic = PuzzleSolver.prototype.permutationHeuristic;

PuzzleSolver.prototype.allMoves = function() {
  var moves = [];
  for (var i=0; i<this.model.pieces.length; ++i) {
    var piece = this.model.pieces[i];
    var cur_piece_moves = this.model.getMoves(piece);
    for (var j=0; j<cur_piece_moves.length; ++j) {
      moves.push({piece: piece, move: cur_piece_moves[j]});
    }
  }
  return moves;
};

PuzzleSolver.prototype.applyMove = function(move) {
  this.model.movePiece(move.piece, move.move.x, move.move.y);
};

PuzzleSolver.prototype.undoMove = function(move) {
  this.model.movePiece(move.piece, -move.move.x, -move.move.y);
};

PuzzleSolver.prototype.isInverseOf = function(move, prev_move) {
  if (prev_move === null) return false;
  if (move.piece !== prev_move.piece) return false;
  return move.x === -prev_move.x && move.y === -prev_move.y;
};

PuzzleSolver.prototype.bruteDFS = function(max_depth) {
  var solver = this;
  var min_heuristic = this.heuristic();
  var best_moves = [];

  function search(move_sequence) {
    var moves = solver.allMoves();
    var depth = move_sequence.length;

    var heur = solver.heuristic();
    if (heur < min_heuristic) {
      min_heuristic = heur;
      best_moves = move_sequence.slice();
    }

    if (depth === max_depth) return;

    var prev_move = null;
    if (depth > 0) prev_move = move_sequence[depth-1];

    for (var i=0; i<moves.length; ++i) {
      var move = moves[i];
      if (solver.isInverseOf(move, prev_move)) continue;
      solver.applyMove(move);
      move_sequence.push(move);
      search(move_sequence);
      solver.undoMove(move_sequence.pop());
    }
  }

  search([]);

  return best_moves;
};

PuzzleSolver.prototype.IDAStar = function(depth_limit) {
  var solver = this;

  var min_heuristic = this.heuristic();
  var best_moves = [];

  function search(move_sequence, max_depth) {
    var moves = solver.allMoves();
    var depth = move_sequence.length;

    var h = solver.heuristic();

    if (h < min_heuristic) {
      min_heuristic = h;
      best_moves = move_sequence.slice();
    }
    if (min_heuristic === 0) return;

    if (h > max_depth-depth) return;

    var prev_move = null;
    if (depth > 0) prev_move = move_sequence[depth-1];

    for (var i=0; i<moves.length; ++i) {
      var move = moves[i];
      if (solver.isInverseOf(move, prev_move)) continue;
      solver.applyMove(move);
      move_sequence.push(move);
      search(move_sequence, max_depth);
      solver.undoMove(move_sequence.pop());
    }
  }

  for (var max_depth=0; max_depth <= depth_limit; ++max_depth) {
    console.log(max_depth);
    search([], max_depth);
    console.log(min_heuristic);
    if (min_heuristic === 0) break;
  }

  return best_moves;
};

PuzzleSolver.prototype.solve = function() {
  return this.IDAStar(12);
};
