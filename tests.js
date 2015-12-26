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
  assert.equal( solver.pieces_by_id[1].length, 6 );
  assert.equal( solver.pieces_by_id[1][0].color, 'blue' );
  assert.equal( solver.piece_permutations[1].length, 720 );
});

QUnit.test("clones", function( assert ) {
  var puzzle = new PuzzleModel();
  puzzle.movePiece(puzzle.pieces[0], 0, -1);
  var clone = puzzle.clone();

  assert.deepEqual(clone.pieces[0].position, puzzle.pieces[0].position);
  clone.movePiece(clone.pieces[0], 0, 1);

  assert.ok(clone.pieces[0].position.y != puzzle.pieces[0].position.y);

  var subset = puzzle.selectSubset(function (piece) {
    return piece.color == 'blue';
  });

  var subset2 = subset.selectSubset(function (piece) {
    return piece.color == 'blue';
  });

  assert.equal(subset.pieces.length, 6);
  assert.equal(subset2.pieces.length, 6);
});

QUnit.test( "red partial solution", function( assert ) {
  var red_piece = (new PuzzleModel()).selectSubset(function (piece) {
    return piece.color == 'red';
  });

  assert.equal(red_piece.pieces.length, 1, 'red subset has one piece');
  var solver = new PuzzleSolver(red_piece);
  assert.equal(solver.heuristic(), 7, 'initial heuristic');

  var solution = solver.solve();
  assert.equal(solution.length, 7, 'solution length');

  red_piece.moveSequence(solution);
  assert.equal(solver.heuristic(), 0, 'final solution has heuristic 0');
});

QUnit.test( "piece 1 partial solution", function( assert ) {

  var subproblem = (new PuzzleSolver(new PuzzleModel())).pieceIdSubproblem(1);
  assert.ok(subproblem.pieces_by_id[1].length, 6);

  assert.ok(subproblem.heuristic() > 0, 'initial heuristic > 0');
  var solution = subproblem.solve();

  subproblem.model.moveSequence(solution);
  assert.equal(subproblem.heuristic(), 0, 'final solution has heuristic 0');
});

QUnit.test( "all partial color solutions", function( assert ) {

  var colors = ['red', 'blue', 'yellow', 'white'];

  function getSubset(color) {
    return (new PuzzleModel()).selectSubset(function (piece) {
      return piece.color === color;
    });
  }

  for (var i in colors) {

    var subset = getSubset(colors[i]);
    assert.ok(subset.pieces.length > 0);

    var solver = new PuzzleSolver(subset);
    assert.ok(solver.heuristic() > 0, 'initial heuristic > 0');

    var solution = solver.solve();

    subset.moveSequence(solution);
    assert.equal(solver.heuristic(), 0, 'final solution has heuristic 0');
  }
});


QUnit.test( "permutations", function( assert ) {
  assert.deepEqual( PuzzleSolver.permutationsOf(['a','b']), [['a','b'],['b','a']] );

  assert.deepEqual( PuzzleSolver.permutationsOf([1,2,3]), [
    [1,2,3], [1,3,2], [2,1,3], [2,3,1], [3,1,2], [3,2,1]
  ]);

  assert.equal( PuzzleSolver.permutationsOf([1,2,3,4,5,6]).length, 720);
});
