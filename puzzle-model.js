"use strict";

function PuzzleModel() {
  var model = this;

  this.width = 6;
  this.height = 5;

  this.pieces = [];
  this.number_of_different_pieces = 0;

  function pairToXY(p) { return { x: p[0], y: p[1] }; }

  function Piece(id, shape, color, initial_position) {
    this.id = id;
    this.shape = shape.map(pairToXY);
    this.color = color;
    this.position = {
      x: initial_position[0],
      y: initial_position[1]
    };
  }

  function definePiece(shape, color, initial_positions, final_positions) {
    var id = model.number_of_different_pieces++;
    final_positions = final_positions.map(pairToXY);
    for (var i in initial_positions) {
      var piece = new Piece(id, shape, color, initial_positions[i]);
      piece.final_positions = final_positions;
      model.pieces.push(piece);
    }
  }

  definePiece([[0,0], [1,0], [1,1], [0,1]], 'red', [
    [4,3]
  ], [
    [0,0]
  ]);
  definePiece([[0,0]], 'blue', [
    [2,2], [3,2],
    [2,3], [3,3],
    [2,4], [3,4]
  ],[
    [2,0], [3,0],
    [0,3], [1,3],
    [4,3], [5,3]
  ]);
  definePiece([[0,0],[1,0]], 'yellow', [
    [0,2], [0,3], [0,4]
  ], [
    [0,4], [2,4], [4,4]
  ]);
  definePiece([[0,0],[1,0],[0,1]], 'white', [
    [0,0], [3,0]
  ], [
    [2,1], [4,0]
  ]);
  definePiece([[1,1],[1,0],[0,1]], 'white', [
    [1,0], [4,0]
  ], [
    [2,2], [4,1]
  ]);

  var board = new PuzzleModel.Board(this);

  this.getMoves = function(piece) {
    return board.getMoves(piece);
  };

  this.canMove = function(piece) {
    return this.getMoves(piece).length > 0;
  };

  this.movePiece = function(piece, dx, dy) {
    if (!board.canMove(piece,dx,dy)) throw("Illegal move");
    piece.position.x += dx;
    piece.position.y += dy;
  };
}

PuzzleModel.prototype.moveSequence = function(move_seq) {
  for (var i in move_seq) {
    var move = move_seq[i];
    this.movePiece(move.piece, move.move.x, move.move.y);
  }
};

PuzzleModel.prototype.clone = function() {
  var clone = new PuzzleModel();
  var new_pieces = [];
  for (var i=0; i<this.pieces.length; ++i) {
    var piece = clone.pieces[i];
    piece.position.x = this.pieces[i].position.x;
    piece.position.y = this.pieces[i].position.y;
    new_pieces.push(piece);
  }
  clone.pieces = new_pieces;
  return clone;
};

PuzzleModel.prototype.selectSubset = function(filter_func) {
  var clone = this.clone();
  clone.pieces = clone.pieces.filter(filter_func);
  return clone;
};

PuzzleModel.Board = function (puzzle_model) {

  function emptyBoard() {
    var board = [];
    for (var i=0; i<puzzle_model.width*puzzle_model.height; ++i)
      board.push(null);
    return board;
  }

  function placeBlock(board, x, y, piece) {
    board[puzzle_model.width*y + x] = piece;
  }

  function getBlock(board, x, y, piece) {
    return board[puzzle_model.width*y + x];
  }

  function placePiece(board, piece) {
    for (var i in piece.shape) {
      var x = piece.position.x + piece.shape[i].x;
      var y = piece.position.y + piece.shape[i].y;
      placeBlock(board,x,y,piece);
    }
  }

  function canPlace(board, piece, dx, dy) {
    for (var i in piece.shape) {
      var x = piece.position.x + piece.shape[i].x + dx;
      var y = piece.position.y + piece.shape[i].y + dy;
      var block = getBlock(board,x,y);
      if (x < 0 || x >= puzzle_model.width) return false;
      if (y < 0 || y >= puzzle_model.height) return false;
      if (block !== null && block !== piece) return false;
    }
    return true;
  }

  function fillBoard() {
    var board = emptyBoard();
    for (var i in puzzle_model.pieces) {
      placePiece(board, puzzle_model.pieces[i]);
    }
    return board;
  }

  this.getMoves = function(piece) {
    var board = fillBoard();
    var moves = [];
    for (var dx=-1; dx<=1; dx++) {
      for (var dy=-1; dy<=1; dy++) {
        if (Math.abs(dx)+Math.abs(dy) === 1 && canPlace(board, piece, dx, dy)) {
          moves.push({x: dx, y: dy});
        }
      }
    }
    return moves;
  };

  this.canMove = function(piece, dx, dy) {
    var board = fillBoard();
    return canPlace(board, piece, dx, dy);
  };
};
