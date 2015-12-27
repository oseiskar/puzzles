"use strict";
/*global FibonacciHeap:false */

function PuzzleSolver(puzzle, parent) {
  this.model = puzzle;
  this.pieces_by_id = {};
  this.subproblem_map = {};

  this.cache_queries = 0;
  this.cache_misses = 0;

  if (parent) {
    this.subproblem_map = parent.subproblem_map;
  }

  for (var i in puzzle.pieces) {
    var id = puzzle.pieces[i].id;
    if (!this.pieces_by_id[id]) {
      this.pieces_by_id[id] = [];
      this.subproblem_map[id] = {};
    }

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

PuzzleSolver.prototype.getSubproblem = function(filter_func) {
  var puzzle_subset = this.model.selectSubset(filter_func);
  return new PuzzleSolver(puzzle_subset, this);
};

PuzzleSolver.prototype.pieceIdSubproblem = function(piece_id) {
  piece_id = parseInt(piece_id);
  var subproblem = this.getSubproblem(function(piece) {
    return piece.id === piece_id;
  });
  subproblem.heuristic = PuzzleSolver.prototype.permutationHeuristic;
  return subproblem;
};

PuzzleSolver.prototype.pieceIdSubproblemSolutionLength = function(piece_id) {

  if (!(piece_id in this.subproblem_map)) return 0;

  var bitmasks = this.subproblem_map[piece_id];
  var piece_bitmask = this.model.stateBitmasks()[piece_id];

  this.cache_queries++;

  if (!(piece_bitmask in bitmasks)) {
    var subproblem = this.pieceIdSubproblem(piece_id);
    this.cache_misses++;
    bitmasks[piece_bitmask] = subproblem.IDAStar().length;
  }
  return bitmasks[piece_bitmask];
};

PuzzleSolver.prototype.subproblemHeuristic = function() {
  var min_moves = 0;

  for (var id in this.pieces_by_id) {
    min_moves += this.pieceIdSubproblemSolutionLength(id);
  }
  return min_moves;
};

PuzzleSolver.prototype.noBlueHeuristic = function() {
  var blue_id = 1;
  var blue = this.pieceIdSubproblemSolutionLength(blue_id);
  var no_blue_solver = this.getSubproblem(function(piece) {
    return piece.id !== blue_id;
  });
  no_blue_solver.heuristic = PuzzleSolver.prototype.subproblemHeuristic;
  return blue + no_blue_solver.IDAStar().length;
};

//PuzzleSolver.prototype.heuristic = PuzzleSolver.prototype.minHeuristic;
PuzzleSolver.prototype.heuristic = PuzzleSolver.prototype.permutationHeuristic;
//PuzzleSolver.prototype.heuristic = PuzzleSolver.prototype.subproblemHeuristic;
//PuzzleSolver.prototype.heuristic = PuzzleSolver.prototype.noBlueHeuristic;

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

PuzzleSolver.prototype.dijkstra = function() {

  var max_frontier_size = 10000;

  var frontier = [this.model];
  var shortest_paths = {};
  shortest_paths[this.model.stateString()] = [];

  while (frontier.length > 0) {
    var node = frontier.shift();
    var node_id = node.stateString();
    var path = shortest_paths[node_id];

    if (frontier.length > max_frontier_size)
      throw "max frontier size exceeded";

    PuzzleSolver.applyEvaluationLimit();

    var solver = new PuzzleSolver(node);

    if (solver.minHeuristic() === 0)
      return this.reconstructPath(path);

    var moves = solver.allMoves();
    for (var i in moves) {
      var move = moves[i];
      solver.applyMove(move);
      var next_node_id = node.stateString();
      if (!(next_node_id in shortest_paths)) {
        shortest_paths[next_node_id] = path.concat([move]);
        frontier.push(node.clone());
      } else if (shortest_paths[next_node_id].length > path.length+1) {
        shortest_paths[next_node_id] = path.concat([move]);
      }
      solver.undoMove(move);
    }
  }

  throw "goal not found";
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

PuzzleSolver.prototype.IDAStar = function(depth_limit) {
  var solver = this;

  var min_heuristic = this.heuristic();
  var best_moves = [];

  function search(move_sequence, max_depth) {
    var moves = solver.allMoves();
    var depth = move_sequence.length;

    var h = solver.heuristic();
    PuzzleSolver.applyEvaluationLimit();

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

  for (var max_depth=0; !depth_limit || max_depth <= depth_limit; ++max_depth) {
    search([], max_depth);
    if (this.heuristic === PuzzleSolver.prototype.heuristic) {
      console.log(max_depth + " -> " + min_heuristic + ", "
        + this.cache_misses + "/" + this.cache_queries + " "
        + PuzzleSolver.applyEvaluationLimit());
    }
    if (min_heuristic === 0) break;
  }

  return best_moves;
};

PuzzleSolver.prototype.solve = function() {
  return this.AStar();
};
