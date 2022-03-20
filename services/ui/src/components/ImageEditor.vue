<template>
<div>
  <canvas @click="onClick" class="max-w-full" ref="canvas">
  </canvas>
</div>
</template>

<script>
import FastAverageColor from 'fast-average-color';

export default {
  props: {
    src: String,
    lineWidth: {
      default: 5,
    },
    circleRadius: {
      default: 7,
    },
    color: {
      default: '#cc3300',
    },
  },
  data() {
    return {
      image: null,
      drawing: true,
      drawingPoints: [],
    };
  },
  mounted() {
    this.loadImage();
  },
  watch: {
    src() {
      this.loadImage();
    },
    image() {
      this.refreshCanvas();
    },
  },
  methods: {
    loadImage() {
      const image = new Image();
      image.setAttribute('crossorigin', 'anonymous');
      image.onload = () => {
        this.image = image;
      };
      image.src = this.src;
    },
    refreshCanvas() {
      if (!this.$refs.canvas) {
        return;
      }

      this.drawingPoints = [];
      let ctx = this.$refs.canvas.getContext('2d');
      ctx.clearRect(0, 0, this.$refs.canvas.width, this.$refs.canvas.height);

      if (!this.image) {
        return;
      }

      ctx = this.$refs.canvas.getContext('2d');
      this.$refs.canvas.width = this.image.width;
      this.$refs.canvas.height = this.image.height;
      ctx.drawImage(this.image, 0, 0);
    },
    getAverageColor() {
      const fac = new FastAverageColor();
      return fac.getColor(this.image).hex;
    },
    saveDrawShapeAsWKT() {
      let xCoords = this.drawingPoints.map((point) => point[0]);
      let yCoords = this.drawingPoints.map((point) => point[1]);

      let xCenter = 0;
      let yCenter = 0;
      let area = 0;

      let i = 0;
      let a = 0;
      for (i = 0; i < xCoords.length - 1; i += 1) {
        a = xCoords[i] * yCoords[i + 1] - xCoords[i + 1] * yCoords[i];
        area += a;
        xCenter += (xCoords[i] + xCoords[i + 1]) * a;
        yCenter += (yCoords[i] + yCoords[i + 1]) * a;
      }
      a = xCoords[i] * yCoords[0] - xCoords[0] * yCoords[i];
      area += a;
      xCenter += (xCoords[i] + xCoords[0]) * a;
      yCenter += (yCoords[i] + yCoords[0]) * a;

      xCenter /= (area * 6 * 0.5);
      yCenter /= (area * 6 * 0.5);

      xCoords = xCoords.map((x) => x - xCenter);
      yCoords = yCoords.map((y) => y - yCenter);

      const xMin = Math.min(...xCoords);
      const yMin = Math.min(...yCoords);
      const xMax = Math.max(...xCoords);
      const yMax = Math.max(...yCoords);

      const normFactor = Math.max(
        Math.abs(xMin),
        Math.abs(yMin),
        Math.abs(xMax),
        Math.abs(yMax),
      );

      xCoords = xCoords.map((x) => x / normFactor);
      yCoords = yCoords.map((y) => y / normFactor);

      const points = xCoords.map((x, idx) => [x, -yCoords[idx]]);
      points.push(points[0]); // close polygon

      const wktCoords = points.map(([x, y]) => `${x} ${y}`).join(', ');
      const wkt = `POLYGON((${wktCoords}))`;

      return wkt;
    },
    startDrawing() {
      this.refreshCanvas();

      this.drawingPoints = [];
      this.drawing = true;
    },
    resetDrawing() {
      this.refreshCanvas();
      this.drawingPoints = [];
    },
    undoDrawing() {
      if (this.drawingPoints.length > 0) {
        this.drawingPoints.pop();
      }
      const oldDrawingPoints = this.drawingPoints.slice();
      console.log(oldDrawingPoints);

      this.refreshCanvas();

      oldDrawingPoints.forEach(([x, y]) => this.addPoint(x, y));
    },
    endDrawing() {
      this.drawing = false;
    },
    onClick(event) {
      if (!this.drawing) {
        return;
      }

      const bounds = this.$refs.canvas.getBoundingClientRect();

      const scaleX = this.$refs.canvas.width / bounds.width;
      const scaleY = this.$refs.canvas.height / bounds.height;

      const x = (event.clientX - bounds.left) * scaleX;
      const y = (event.clientY - bounds.top) * scaleY;

      this.addPoint(x, y);
    },
    addPoint(x, y) {
      this.drawingPoints.push([x, y]);

      const ctx = this.$refs.canvas.getContext('2d');

      const bounds = this.$refs.canvas.getBoundingClientRect();

      const scaleX = this.$refs.canvas.width / bounds.width;
      const scaleY = this.$refs.canvas.height / bounds.height;
      const scale = Math.max(scaleX, scaleY);

      const [x1, y1] = this.drawingPoints.at(-1);

      ctx.fillStyle = this.color;

      ctx.beginPath();
      ctx.arc(x1, y1, this.circleRadius * scale, 0, 2 * Math.PI);
      ctx.fill();

      if (this.drawingPoints.length >= 2) {
        const [x0, y0] = this.drawingPoints.at(-2);

        ctx.strokeStyle = this.color;
        ctx.lineWidth = this.lineWidth * scale;

        ctx.beginPath();
        ctx.moveTo(x0, y0);
        ctx.lineTo(x1, y1);
        ctx.stroke();
      }
    },
  },
};
</script>

<style scoped>
</style>
