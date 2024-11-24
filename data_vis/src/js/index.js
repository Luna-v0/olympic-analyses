import * as d3 from 'd3';
import '../main.css';
console.log('Home page script loaded');


const svg = d3.select("#hello_world")
  .append("svg")
  .attr("width", 200)
  .attr("height", 200)
  .classed("bg-gray-200", true); // Tailwind class for background color

svg.append("circle")
  .attr("cx", 100)
  .attr("cy", 100)
  .attr("r", 50)
  .attr("fill", "steelblue");