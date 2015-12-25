"use strict";

function PuzzleSolver(puzzle) {
  this.model = puzzle;
}

PuzzleSolver.prototype.heuristic = function() {
  var red_piece = this.model.pieces[0];
  return red_piece.position.x + red_piece.position.y;
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

PuzzleSolver.prototype.bruteForce = function(max_depth) {
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

PuzzleSolver.prototype.solve = function() {
  return this.bruteForce(8);
};
