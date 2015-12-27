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
  /*this.model = this.model.selectSubset(function(p){
    return p.color=='blue' || p.color=='yellow';
  });*/
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
  setTimeout(function() {
    var solution = view.solver.solve();
    view.playSolution(solution);
  }, 1000);
}

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

PuzzleView.prototype.playSolution = function(solution) {

  if (solution.length === 0) return;
  var move = solution.shift();

  this.model.movePiece(move.piece, move.move.x, move.move.y);
  this.render();

  var that = this;
  setTimeout(function() {
    that.playSolution(solution);
  }, 1000);
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

  this.model.movePiece(this.selected_piece, move.x, move.y);
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
