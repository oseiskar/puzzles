"use strict";

function PuzzleSolver(puzzle) {
  this.model = puzzle;
}

PuzzleSolver.prototype.heuristic = function() {
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
  return this.IDAStar(30);
};
