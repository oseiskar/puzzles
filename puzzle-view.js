"use strict";
/*global d3:false */
/*global PuzzleModel:false */

var SvgPath = {
    p: function (x,y) { return x + ',' + y + ' '; },
    moveTo: function (x,y) { return 'M' + SvgPath.p(x,y); },
    lineTo: function (x,y) { return 'L' + SvgPath.p(x,y); },
    curveTo: function (ctrl1x, ctrl1y, ctrl2x, ctrl2y, x, y) {
        return 'C' +
            SvgPath.p(ctrl1x, ctrl1y) +
            SvgPath.p(ctrl2x, ctrl2y) +
            SvgPath.p(x,y);
    },
    close: 'Z'
};

function PuzzleView() {

    var view = this;
    this.model = new PuzzleModel();

    this.style = {
      canvas: {
          width: 1600,
          height: 700
      }
    };

    this.d3root = d3.select('#tree')
        .attr('viewBox', '0 0 '+this.style.canvas.width+' '+this.style.canvas.height)
        .append('g')
        .attr('transform', 'translate(0,' + (this.style.canvas.height/2) + ')' )
        .append('g');
}

PuzzleView.prototype.render = function () {
    var view = this;
};
