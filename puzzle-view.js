"use strict";
/*global d3:false */
/*global PuzzleModel:false */

function PuzzleView() {

    var view = this;
    this.model = new PuzzleModel();

    this.d3root = d3.select('#puzzle')
        .attr('viewBox', '0 0 '+this.model.width+' '+this.model.height)
        .append('g');

    this.d3root.append('rect')
      .attr('x', 0).attr('y', 0)
      .attr('width', this.model.width)
      .attr('height', this.model.height)
      .attr('class', 'board');

    this.render();
}

PuzzleView.prototype.render = function () {
    var view = this;

    var pieces = this.d3root.selectAll('g.piece')
      .data(this.model.pieces);

    var new_pieces = pieces
      .enter()
      .append('g')
      .attr('class', 'piece');

    this.renderPieces(new_pieces);

    pieces.attr('transform', function(piece) {
        return 'translate(' + piece.position.x + ',' + piece.position.y + ')';
      });
};

PuzzleView.prototype.renderPieces = function(d3_selector) {

  function generateMiddlePieces(piece_shape) {
    var all_pieces = [];
    for (var i in piece_shape) {
      var cur = piece_shape[i];
      all_pieces.push(cur);
      var prev = piece_shape[piece_shape.length-1];
      if (i > 0) prev = piece_shape[i-1];
      var dx = cur[0]-prev[0];
      var dy = cur[1]-prev[1];
      if (dx === 0 || dy === 0) {
        all_pieces.push([prev[0]+dx*0.5, prev[1]+dy*0.5]);
      }
    }
    return all_pieces;
  }

  var PADDING = 0.04;

  d3_selector
    .selectAll('rect')
    .data(function (piece) { return generateMiddlePieces(piece.shape); })
    .enter()
    .append('rect')
    .attr('width', 1-PADDING*2).attr('height', 1-PADDING*2)
    .attr('x', function(shape) { return shape[0]+PADDING; })
    .attr('y', function(shape) { return shape[1]+PADDING; })
    .attr('class', 'block-base');

  d3_selector
    .selectAll('circle')
    .data(function(piece) { return piece.shape; })
    .enter()
    .append('circle')
    .attr('r', 0.2)
    .attr('cx', function(shape) { return shape[0]+0.5; })
    .attr('cy', function(shape) { return shape[1]+0.5; })
    .attr('fill', function(shape) {
      return d3.select(this.parentNode).datum().color;
    });
};
