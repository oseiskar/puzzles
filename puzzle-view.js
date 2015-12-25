"use strict";
/*global d3:false */
/*global PuzzleModel:false */

function PuzzleView() {

    var view = this;
    this.model = new PuzzleModel();

    this.d3root = d3.select('#puzzle')
        .attr('viewBox', '0 0 '+this.model.width+' '+this.model.height)
        .append('g');

    this.render();
}

PuzzleView.prototype.render = function () {
    var view = this;

    this.d3root.selectAll('g.piece')
      .data(this.model.pieces)
      .enter()
      .append('g')
      .attr('class', 'piece')
      .attr('transform', function(piece) {
        return 'translate(' + piece.position.x + ',' + piece.position.y + ')';
      })
      .selectAll('rect')
      .data(function (piece) { return piece.shape; })
      .enter()
      .append('rect')
      .attr('width', 1).attr('height', 1)
      .attr('x', function(shape) { return shape[0]; })
      .attr('y', function(shape) { return shape[1]; })
      .attr('style', function(shape) {
        return 'fill: ' + d3.select(this.parentNode).datum().color + "; " +
          'stroke: black; stroke-width: 0.02;';
      });
};
