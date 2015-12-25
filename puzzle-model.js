"use strict";

function PuzzleModel() {
  var model = this;

  this.width = 6;
  this.height = 5;

  this.pieces = [];

  function Piece(id, shape, color, initial_position) {
    this.id = id;
    this.shape = shape;
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

  definePiece([[0,0], [1,0], [0,1], [1,1]], 'red', [
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
}
