"use strict";

function PuzzleModel() {
  var model = this;

  this.width = 6;
  this.height = 5;

  this.pieces = [];
  this.max_id = 0;

  function pairToXY(p) { return { x: p[0], y: p[1] }; }

  function Piece(id, index, shape, color, position, final_positions) {
    this.id = id;
    this.index = index;
    this.shape = shape;
    this.color = color;
    this.final_positions = final_positions;
    this.position = { // deep copy
      x: position.x,
      y: position.y
    };
  }

  Piece.prototype.clone = function() {
    return new Piece(this.id, this.index, this.shape, this.color,
      this.position, this.final_positions);
  };

  Piece.prototype.positionIndex = function() {
    return this.position.y * model.width + this.position.x;
  };

  Piece.prototype.bitmask = function() {
    return 1 << this.positionIndex();
  };

  function definePiece(shape, color, initial_positions, final_positions) {
    var id = model.max_id++;
    shape = shape.map(pairToXY);
    final_positions = final_positions.map(pairToXY);
    initial_positions = initial_positions.map(pairToXY);

    for (var i in initial_positions) {
      var piece = new Piece(id, model.pieces.length, shape, color,
        initial_positions[i], final_positions);
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

  this.getAllMoves = function(piece) {
    return board.getAllMoves(piece);
  };

  this.canMove = function(piece) {
    return this.getMoves(piece).length > 0;
  };

  this.movePieceUnchecked = function(piece, dx, dy) {
    piece.position.x += dx;
    piece.position.y += dy;
  };

  this.movePiece = function(piece, dx, dy) {
    if (!board.canMove(piece,dx,dy)) throw("Illegal move");
    model.movePieceUnchecked(piece,dx,dy);
  };
}

PuzzleModel.prototype.stateBitmasks = function() {
  var bitmasks = {};
  for (var i in this.pieces) {
    var piece = this.pieces[i];
    if (!bitmasks[piece.id]) bitmasks[piece.id] = 0;
    bitmasks[piece.id] = bitmasks[piece.id] | piece.bitmask();
  }
  return bitmasks;
};

PuzzleModel.prototype.stateString = function() {
  var bitmasks = this.stateBitmasks();
  var str = '';
  for (var i=0; i<this.max_id; ++i)
    if (i in bitmasks) {
      str = str + i + '(' + bitmasks[i] + ')';
    }
  return str;
};

PuzzleModel.prototype.moveSequence = function(move_seq) {
  for (var i in move_seq) {
    var move = move_seq[i];
    this.movePiece(move.piece, move.move.x, move.move.y);
  }
};

PuzzleModel.prototype.clone = function() {
  var clone = new PuzzleModel();
  clone.pieces = this.pieces.map(function (p) { return p.clone(); });
  return clone;
};

PuzzleModel.prototype.selectSubset = function(filter_func) {
  var clone = this.clone();
  clone.pieces = clone.pieces.filter(filter_func);
  return clone;
};

PuzzleModel.Board = function (puzzle_model) {

  var board = PuzzleModel.Board.board;
  if (!board) {
    board = [];
    for (var i=0; i<puzzle_model.width*puzzle_model.height; ++i)
      board.push(null);
    PuzzleModel.Board.board = board;
  }

  function emptyBoard() {
    for (var j in PuzzleModel.Board.board)
      PuzzleModel.Board.board[j] = null;
    return PuzzleModel.Board.board;
  }

  function placeBlock(x, y, piece) {
    board[puzzle_model.width*y + x] = piece;
  }

  function getBlock(x, y, piece) {
    return board[puzzle_model.width*y + x];
  }

  function placePiece(piece) {
    for (var i in piece.shape) {
      var x = piece.position.x + piece.shape[i].x;
      var y = piece.position.y + piece.shape[i].y;
      placeBlock(x,y,piece);
    }
  }

  function canPlace(piece, dx, dy) {
    for (var i in piece.shape) {
      var x = piece.position.x + piece.shape[i].x + dx;
      var y = piece.position.y + piece.shape[i].y + dy;
      var block = getBlock(x,y);
      if (x < 0 || x >= puzzle_model.width) return false;
      if (y < 0 || y >= puzzle_model.height) return false;
      if (block !== null && block !== piece) return false;
    }
    return true;
  }

  function fillBoard() {
    emptyBoard();
    for (var i in puzzle_model.pieces) {
      placePiece(puzzle_model.pieces[i]);
    }
  }

  function getMovesUnfilled(piece) {
    var moves = [];
    for (var dx=-1; dx<=1; dx++) {
      for (var dy=-1; dy<=1; dy++) {
        if (Math.abs(dx)+Math.abs(dy) === 1 && canPlace(piece, dx, dy)) {
          moves.push({x: dx, y: dy});
        }
      }
    }
    return moves;
  }

  this.getMoves = function(piece) {
    fillBoard();
    return getMovesUnfilled(piece);
  };

  this.getAllMoves = function() {
    fillBoard();
    var moves = [];
    for (var i in puzzle_model.pieces) {
      var piece = puzzle_model.pieces[i];
      var cur_moves = getMovesUnfilled(piece);
      for (var j in cur_moves) {
        moves.push({
          piece: piece,
          move: cur_moves[j]
        });
      }
    }
    return moves;
  };

  this.canMove = function(piece, dx, dy) {
    fillBoard();
    return canPlace(piece, dx, dy);
  };
};
