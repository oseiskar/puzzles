"use strict";
/*global d3:false */
/*global PuzzleModel:false */
/*global PuzzleSolver:false */
/*global setTimeout:false */

function PuzzleView() {

  this.selected_piece_group = null;
  this.selected_piece = null;
  this.prev_move = null;

  var view = this;
  this.model = new PuzzleModel();
  this.solver = new PuzzleSolver(this.model);

  this.d3root = d3.select('#puzzle')
    .attr('viewBox', '0 0 '+this.model.width+' '+this.model.height)
    .append('g');

  this.d3root.append('rect')
    .attr('x', 0).attr('y', 0)
    .attr('width', this.model.width)
    .attr('height', this.model.height)
    .attr('class', 'board')
    .on('click', function() { view.onBoardClick(); });

  this.render();

  this.solution_view = new SolutionView(this);
}

function SolutionView(puzzle_view) {

  var solution_view = this;
  this.puzzle_view = puzzle_view;

  this.solution_controls = d3.select('#solution-controls');

  this.buttons = {};
  var actions = ['solve', 'play', 'stop', 'next', 'prev'];
  function makeAction(action) {
    return (function() {
      solution_view[action]();
      solution_view.render();
    });
  }

  for (var i in actions) {
    var action = actions[i];
    this.buttons[action] = d3.select('#'+action);
    this.buttons[action].on('click', makeAction(action));
  }

  this.clear();
}

SolutionView.prototype.setSolution = function(solution) {
  this.solution = solution;
  this.buttons.solve.classed('hidden', true);
  this.solution_controls.classed('hidden', false);
};

SolutionView.prototype.clear = function(solution) {
  this.solution = null;
  this.solution_index = 0;
  this.playing = false;

  this.buttons.solve.classed('hidden', false);
  this.solution_controls.classed('hidden', true);
};

SolutionView.prototype.solve = function() {
  var solution = this.puzzle_view.solver.solve();
  this.setSolution(solution);
};

SolutionView.prototype.next = function(solution) {
  if (this.solution_index >= this.solution.length) return;
  var move = this.solution[this.solution_index++];
  this.puzzle_view.movePiece(move.piece, move.move.x, move.move.y);
  this.puzzle_view.render();

  if (this.playing) {
    this.render();
    var that = this;
    setTimeout(function() { that.next(); }, 1000);
  }
};

SolutionView.prototype.prev = function(solution) {
  if (this.solution_index === 0) return;
  this.solution_index--;
  var move = this.solution[this.solution_index];
  this.puzzle_view.movePiece(move.piece, -move.move.x, -move.move.y);
  this.puzzle_view.render();
};

SolutionView.prototype.play = function(solution) {
  if (this.solution_index >= this.solution.length) return this.stop();
  this.playing = true;
  this.next();
};

SolutionView.prototype.render = function() {
  this.solution_controls.select('#step-counter').text(
    (this.solution_index+1) + ' / ' + this.solution.length
  );
  this.buttons.play.classed('hidden', this.playing);
  this.buttons.next.classed('hidden', this.playing);
  this.buttons.prev.classed('hidden', this.playing);
  this.buttons.stop.classed('hidden', !this.playing);
};

SolutionView.prototype.stop = function(solution) {
  this.playing = false;
};

PuzzleView.prototype.render = function () {

  var pieces = this.d3root.selectAll('g.piece')
    .data(this.model.pieces);

  var new_pieces = pieces
    .enter()
    .append('g')
    .attr('class', 'piece');

  this.renderPieces(new_pieces);

  pieces
    .transition()
    .attr('transform', function(piece) {
      return 'translate(' + piece.position.x + ',' + piece.position.y + ')';
    });
};

PuzzleView.prototype.onPieceClick = function (piece_group) {

  if (this.selected_piece_group !== null) {
    this.selected_piece_group.classed('selected', false);
  }
  this.selected_piece_group = piece_group;
  piece_group.classed('selected', true);

  this.selected_piece = piece_group.datum();
};

PuzzleView.prototype.onBoardClick = function () {
  if (this.selected_piece === null) return;

  var moves = this.model.getMoves(this.selected_piece);

  if (moves.length === 0) return;

  var move = moves[0];
  if (moves.length > 1 && this.prev_move !== null &&
    this.prev_move.x === -move.x && this.prev_move.y == -move.y)
    move = moves[1];

  this.prev_move = move;

  this.solution_view.clear();
  this.movePiece(this.selected_piece, move.x, move.y);
};

PuzzleView.prototype.movePiece = function(piece, x, y) {
  this.model.movePiece(piece, x, y);
  this.render();
};

PuzzleView.prototype.renderPieces = function(d3_selector) {

  function generateMiddlePieces(piece_shape) {
    var all_pieces = [];
    for (var i in piece_shape) {
      var cur = piece_shape[i];
      all_pieces.push(cur);
      var prev = piece_shape[piece_shape.length-1];
      if (i > 0) prev = piece_shape[i-1];
      var dx = cur.x-prev.x;
      var dy = cur.y-prev.y;
      if (dx === 0 || dy === 0) {
        all_pieces.push({x: prev.x+dx*0.5, y: prev.y+dy*0.5});
      }
    }
    return all_pieces;
  }

  var PADDING = 0.04;

  var view = this;

  d3_selector
    .selectAll('rect')
    .data(function (piece) { return generateMiddlePieces(piece.shape); })
    .enter()
    .append('rect')
    .attr('width', 1-PADDING*2).attr('height', 1-PADDING*2)
    .attr('x', function(block) { return block.x+PADDING; })
    .attr('y', function(block) { return block.y+PADDING; })
    .attr('class', 'block-base')
    .on('click', function() {
      view.onPieceClick(d3.select(this.parentNode));
    });

  d3_selector
    .selectAll('circle')
    .data(function(piece) { return piece.shape; })
    .enter()
    .append('circle')
    .attr('r', 0.2)
    .attr('cx', function(block) { return block.x+0.5; })
    .attr('cy', function(block) { return block.y+0.5; })
    .attr('fill', function(shape) {
      return d3.select(this.parentNode).datum().color;
    })
    .on('click', function() {
      view.onPieceClick(d3.select(this.parentNode));
    });
};
