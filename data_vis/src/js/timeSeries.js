import * as d3 from "d3";
import { apiCall, allKeys } from "./utils";

export function createLineChart({
  selector,
  data,
  lineColors = {},
  margin = { top: 40, right: 30, bottom: 50, left: 50 },
  animationDuration = 1000,
}) {
  // Parse the date as yearly data
  const parseDate = d3.timeParse("%Y");
  data.forEach((d) => {
    d.date = parseDate(d.date); // Convert string years into Date objects
  });

  // Extract line keys dynamically
  const lineKeys = Object.keys(allKeys(data));

  // Fill missing years with `null`
  data = fillMissingYears(data, lineKeys);

  // Define dimensions for the responsive chart
  const container = d3.select(selector).node();
  const containerWidth = container.getBoundingClientRect().width;
  const width = containerWidth - margin.left - margin.right;
  const height = width / 2;

  // Clear any existing SVG
  d3.select(selector).select("svg").remove();

  // Create the SVG container
  const svg = d3
    .select(selector)
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", `translate(${margin.left}, ${margin.top})`);

  // Define X and Y scales
  const x = d3
    .scaleTime()
    .domain(d3.extent(data, (d) => d.date))
    .range([0, width]);

  const y = d3
    .scaleLinear()
    .domain([
      0,
      d3.max(data, (d) => d3.max(lineKeys.map((key) => d.lines[key]))),
    ])
    .nice()
    .range([height, 0]);

  // Add X-axis
  svg
    .append("g")
    .attr("transform", `translate(0, ${height})`)
    .call(d3.axisBottom(x).tickFormat(d3.timeFormat("%Y"))) // Format as years
    .selectAll("text")
    .attr("transform", "rotate(-45)")
    .style("text-anchor", "end");

  // Add Y-axis
  svg.append("g").call(d3.axisLeft(y));

  // Generate lines for each key
  lineKeys.forEach((key) => {
    // Line generator specific to this key
    const lineGenerator = d3
      .line()
      .defined((d) => d.lines[key] !== null) // Skip null values
      .x((d) => x(d.date))
      .y((d) => y(d.lines[key]));

    // Append the line path
    svg
      .append("path")
      .datum(data)
      .attr("fill", "none")
      .attr("stroke", lineColors[key] || "black")
      .attr("stroke-width", 2)
      .attr("d", lineGenerator)
      .attr("stroke-dasharray", function () {
        const totalLength = this.getTotalLength();
        return `${totalLength} ${totalLength}`;
      })
      .attr("stroke-dashoffset", function () {
        return this.getTotalLength();
      })
      .transition()
      .duration(animationDuration)
      .attr("stroke-dashoffset", 0);

    // Add points for each valid data point
    svg
      .selectAll(`circle-${key}`)
      .data(data.filter((d) => d.lines[key] !== null)) // Only valid points
      .enter()
      .append("circle")
      .attr("cx", (d) => x(d.date))
      .attr("cy", (d) => y(d.lines[key]))
      .attr("r", 4)
      .attr("fill", lineColors[key] || "black")
      .style("opacity", 0)
      .transition()
      .delay(animationDuration)
      .style("opacity", 1);
  });

  // Add a legend
  createLegend(svg, lineKeys, lineColors, width, margin);
}

// Helper function to fill missing years
function fillMissingYears(data, lineKeys) {
  // Extract all unique years from the dataset
  const allYears = Array.from(
    new Set(data.map((d) => d.date.getFullYear()))
  ).sort();

  // Fill missing years with null values for all lines
  return allYears.map((year) => {
    const yearData = data.find((d) => d.date.getFullYear() === year);
    const filledLines = {};

    lineKeys.forEach((key) => {
      filledLines[key] = yearData?.lines[key] ?? null; // Use null for gaps
    });

    return {
      date: new Date(year, 0, 1), // Create a Date object for January 1st of each year
      lines: filledLines,
    };
  });
}

// Helper function to create a legend
function createLegend(svg, lineKeys, lineColors, width, margin) {
  const legend = svg.append("g").attr("transform", `translate(0, -30)`);

  lineKeys.forEach((key, i) => {
    const legendItem = legend
      .append("g")
      .attr("transform", `translate(${i * 150}, 0)`);

    legendItem
      .append("rect")
      .attr("width", 15)
      .attr("height", 15)
      .attr("fill", lineColors[key] || "black");

    legendItem
      .append("text")
      .attr("x", 20)
      .attr("y", 12)
      .attr("font-size", "12px")
      .text(`${key}: ${lineColors[key] || "black"}Line`);
  });
}

apiCall({ data: ["1"] }, "http://localhost:8000/api/timeTendencies")
  .then((data) => {
    createLineChart({
      selector: "#timeSeries",
      data: data,
      lineColors: { soccer: "red", shootiing: "blue", tennis: "green" },
    });
  })
  .catch((error) => {
    console.error(error);
  });

window.addEventListener("resize", resize);
