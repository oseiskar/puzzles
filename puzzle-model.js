"use strict";

function PuzzleModel() {
  var model = this;

  this.width = 6;
  this.height = 5;

  this.pieces = [];

  function Piece(id, shape, color, initial_position) {
    this.id = id;
    this.shape = shape.map(function (p) { return { x: p[0], y: p[1] }; });
    this.color = color;
    this.position = {
      x: initial_position[0],
      y: initial_position[1]
    };
  }

  function definePiece(shape, color, initial_positions) {
    var id = model.pieces.length;
    for (var i in initial_positions)
      model.pieces.push(new Piece(id, shape, color, initial_positions[i]));
  }

  definePiece([[0,0], [1,0], [1,1], [0,1]], 'red', [
    [4,3]
  ]);
  definePiece([[0,0]], 'blue', [
    [2,2], [3,2],
    [2,3], [3,3],
    [2,4], [3,4]
  ]);
  definePiece([[0,0],[1,0]], 'yellow', [
    [0,2], [0,3], [0,4]
  ]);
  definePiece([[0,0],[1,0],[0,1]], 'white', [
    [0,0], [3,0]
  ]);
  definePiece([[1,1],[1,0],[0,1]], 'white', [
    [1,0], [4,0]
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
