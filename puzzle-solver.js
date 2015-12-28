"use strict";
/*global FibonacciHeap:false */

function PuzzleSolver(puzzle, parent) {
  this.model = puzzle;
  this.pieces_by_id = {};

  this.cache_queries = 0;
  this.cache_misses = 0;

  for (var i in puzzle.pieces) {
    var id = puzzle.pieces[i].id;
    if (!this.pieces_by_id[id]) {
      this.pieces_by_id[id] = [];
    }
    this.pieces_by_id[id].push(puzzle.pieces[i]);
  }

  if (parent) {
    this.piece_permutations = parent.piece_permutations;
  }
  else {
    this.piece_permutations = {};
    for (i in this.pieces_by_id) {
      this.piece_permutations[i] =
        PuzzleSolver.permutationsOf(this.pieces_by_id[i][0].final_positions);
    }
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

PuzzleSolver.applyEvaluationLimit = (function(){

    var n_evaluations = 0;
    var max_evaluations = 1000000;

    return (function() {
      n_evaluations++;
      if (n_evaluations >= max_evaluations)
        throw "Evaluation limit reached";
      return n_evaluations;
    });
})();

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
      for (var j=0; j<perm.length && j<this.pieces_by_id[id].length; ++j) {
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

//PuzzleSolver.prototype.heuristic = PuzzleSolver.prototype.minHeuristic;
PuzzleSolver.prototype.heuristic = PuzzleSolver.prototype.permutationHeuristic;

PuzzleSolver.prototype.allMoves = function() {
  return this.model.getAllMoves();
};

PuzzleSolver.prototype.applyMove = function(move) {
  this.model.movePieceUnchecked(move.piece, move.move.x, move.move.y);
};

PuzzleSolver.prototype.undoMove = function(move) {
  this.model.movePieceUnchecked(move.piece, -move.move.x, -move.move.y);
};

PuzzleSolver.prototype.isInverseOf = function(move, prev_move) {
  if (prev_move === null) return false;
  if (move.piece !== prev_move.piece) return false;
  return move.x === -prev_move.x && move.y === -prev_move.y;
};

PuzzleSolver.prototype.reconstructPath = function(path) {
    var new_path = [];
    var pieces_by_index = {};
    for (var i=0; i<this.model.pieces.length; ++i) {
      pieces_by_index[this.model.pieces[i].index] = this.model.pieces[i];
    }
    for (i=0; i<path.length; ++i)
      new_path.push({
        piece: pieces_by_index[path[i].piece.index],
        move: path[i].move
      });
    return new_path;
};

PuzzleSolver.prototype.AStar = function() {

  var begin_node = this.model;
  var frontier = new FibonacciHeap();
  frontier.insert(0, begin_node);
  var heap_nodes = {};

  var shortest_paths = {};
  shortest_paths[begin_node.stateString()] = [];

  while (!frontier.isEmpty()) {
    var node = frontier.extractMinimum().value;
    var node_id = node.stateString();
    var path = shortest_paths[node_id];

    PuzzleSolver.applyEvaluationLimit();

    var solver = new PuzzleSolver(node, this);

    if (solver.minHeuristic() === 0)
      return this.reconstructPath(path);

    var moves = solver.allMoves();

    for (var i in moves) {
      var move = moves[i];
      solver.applyMove(move);
      var next_node_id = node.stateString();

      var h = path.length + 1;

      if (!(next_node_id in shortest_paths)) {
        h += solver.heuristic();
        shortest_paths[next_node_id] = path.concat([move]);
        heap_nodes[next_node_id] = frontier.insert(h, node.clone());
      } else if (shortest_paths[next_node_id].length > path.length+1) {
        h += solver.heuristic();
        frontier.decreaseKey(heap_nodes[next_node_id], h);
        shortest_paths[next_node_id] = path.concat([move]);
      }
      solver.undoMove(move);
    }
  }

  throw "goal not found";
};

PuzzleSolver.prototype.solve = function() {
  return this.AStar();
};
