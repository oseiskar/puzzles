"use strict";
/*global QUnit:false */
/*global PuzzleModel:false */
/*global PuzzleSolver:false */

QUnit.test( "starting position", function( assert ) {
  var puzzle = new PuzzleModel();
  var solver = new PuzzleSolver(puzzle);

  assert.ok( solver.heuristic() > 0, "initial heuristic > 0" );
  assert.ok( solver.heuristic() > 20, "initial heuristic > 20" );
  assert.equal( solver.allMoves().length, 3, "3 possible starting moves" );
});

QUnit.test("clones", function( assert ) {
  var puzzle = new PuzzleModel();
  puzzle.movePiece(puzzle.pieces[0], 0, -1);
  var clone = puzzle.clone();

  assert.deepEqual(clone.pieces[0].position, puzzle.pieces[0].position);
  clone.movePiece(clone.pieces[0], 0, 1);

  assert.ok(clone.pieces[0].position.y != puzzle.pieces[0].position.y);
});

QUnit.test( "red partial solution", function( assert ) {
  var red_piece = (new PuzzleModel()).selectSubset(function (piece) {
    return piece.color == 'red';
  });

  assert.equal(red_piece.pieces.length, 1, 'red subset has one piece');
  var solver = new PuzzleSolver(red_piece);
  assert.equal(solver.heuristic(), 7, 'initial heuristic heuristic');

  var solution = solver.solve();
  assert.equal(solution.length, 7, 'solution length');

  red_piece.moveSequence(solution);
  assert.equal(solver.heuristic(), 0, 'final solution has heuristic 0');
});

/*QUnit.test( "blue partial solution", function( assert ) {

  var blue = (new PuzzleModel()).selectSubset(function (piece) {
    return piece.color == 'blue';
  });

  assert.equal(blue.pieces.length, 6, 'blue subset has 6 pieces');
  var solver = new PuzzleSolver(blue);
  assert.ok(solver.heuristic() > 0, 'initial heuristic > 0');

  var solution = solver.solve();

  blue.moveSequence(solution);
  assert.equal(solver.heuristic(), 0, 'final solution has heuristic 0');
});*/
