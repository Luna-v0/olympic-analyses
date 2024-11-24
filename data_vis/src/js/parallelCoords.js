import * as d3 from "d3";

/**
 * Creates or updates a parallel coordinates chart.
 * @param {string} containerId - The ID of the container element (e.g., a <div>) for the chart.
 * @param {Array<Object>} data - The dataset, an array of objects where keys are axis names and values are data points.
 * @param {Array<string>} dimensions - The list of dimensions (keys) to use as axes.
 * @param {Object} highlightInstance - A single data instance to highlight in red.
 */
export function createParallelCoordinatesChart(
  containerId,
  data,
  dimensions,
  highlightInstance = null,
  tooltipField = null
) {
  // Ensure the highlighted instance is included in the data for scale calculation
  const allData = highlightInstance ? [...data, highlightInstance] : data;

  // Get container dimensions using getBoundingClientRect
  const container = document.getElementById(containerId);
  const { width: containerWidth, height: containerHeight } = container.getBoundingClientRect();

  // Set margins and calculate chart dimensions
  const margin = { top: 50, right: 50, bottom: 50, left: 50 };
  const width = containerWidth - margin.left - margin.right;
  const height = containerHeight - margin.top - margin.bottom;

  // Clear any existing SVG
  d3.select(`#${containerId}`).select('svg').remove();

  // Select the container and set up the SVG
  const svg = d3
    .select(`#${containerId}`)
    .append('svg')
    .attr('width', containerWidth)
    .attr('height', containerHeight)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`);

  // Create scales for each dimension
  const yScales = {};
  dimensions.forEach((dim) => {
    const isNumeric = typeof allData[0][dim] === 'number';

    if (isNumeric) {
      // Numerical scale
      yScales[dim] = d3
        .scaleLinear()
        .domain(d3.extent(allData, (d) => d[dim]))
        .range([height, 0]);
    } else {
      // Categorical scale
      yScales[dim] = d3
        .scalePoint()
        .domain([...new Set(allData.map((d) => d[dim]))])
        .range([height, 0])
        .padding(0.5);
    }
  });

  // Create an x-scale for the axes
  const xScale = d3
    .scalePoint()
    .domain(dimensions)
    .range([0, width])
    .padding(1);

  // Line generator
  const linePath = (d) =>
    d3.line()(
      dimensions.map((dim) => [
        xScale(dim),
        yScales[dim](d[dim]),
      ])
    );

  // Create a tooltip
  const tooltip = d3
    .select('body')
    .append('div')
    .style('position', 'absolute')
    .style('background', 'rgba(0, 0, 0, 0.7)')
    .style('color', 'white')
    .style('padding', '5px 10px')
    .style('border-radius', '5px')
    .style('font-size', '12px')
    .style('display', 'none')
    .style('pointer-events', 'none');

  // Draw all lines
  svg
    .selectAll('.line')
    .data(data)
    .enter()
    .append('path')
    .attr('class', 'line')
    .attr('fill', 'none')
    .attr('stroke', '#69b3a2')
    .attr('stroke-width', 1.5)
    .attr('opacity', (d) => d.opacity || 1)
    .attr('d', (d) => linePath(d))
    .on('mouseover', function (event, d) {
      if (tooltipField) {
        tooltip
          .style('display', 'block')
          .html(`Value: ${d[tooltipField]}`);
      }
      d3.select(this).attr('stroke-width', 3);
    })
    .on('mousemove', function (event) {
      tooltip
        .style('top', `${event.pageY + 10}px`)
        .style('left', `${event.pageX + 10}px`);
    })
    .on('mouseout', function () {
      tooltip.style('display', 'none');
      d3.select(this).attr('stroke-width', 1.5);
    });

  // Highlight the specific instance in red with animation
  if (highlightInstance) {
    svg
      .append('path')
      .datum(highlightInstance)
      .attr('class', 'highlight')
      .attr('fill', 'none')
      .attr('stroke', 'red')
      .attr('stroke-width', 2)
      .attr('opacity', 1)
      .attr('d', linePath(highlightInstance))
      .attr('stroke-dasharray', function () {
        const totalLength = this.getTotalLength();
        return `${totalLength} ${totalLength}`;
      })
      .attr('stroke-dashoffset', function () {
        return this.getTotalLength();
      })
      .transition()
      .duration(1500)
      .ease(d3.easeLinear)
      .attr('stroke-dashoffset', 0);
  }

  // Draw axes last to ensure they are on top of the lines
  svg
    .selectAll('.axis')
    .data(dimensions)
    .enter()
    .append('g')
    .attr('class', 'axis')
    .attr('transform', (d) => `translate(${xScale(d)},0)`)
    .each(function (d) {
      d3.select(this).call(d3.axisLeft(yScales[d]));
    })
    .append('text')
    .attr('text-anchor', 'middle')
    .attr('x', 0)
    .attr('y', -10)
    .text((d) => d)
    .style('font-size', '12px')
    .style('fill', 'black');
}