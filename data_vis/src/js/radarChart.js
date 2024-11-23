// radarChart.js
import * as d3 from "d3";

export function createRadarChart({
  selector,
  data,
  options = {},
  margin = { top: 50, right: 80, bottom: 50, left: 80 },
}) {
  const cfg = {
    w: 600, // Width of the circle
    h: 600, // Height of the circle
    levels: 5, // How many levels or inner circles should be drawn
    maxValue: 0, // What is the value that the biggest circle will represent
    labelFactor: 1.25, // How much farther than the radius of the outer circle should the labels be placed
    wrapWidth: 60, // The number of pixels after which a label needs to be given a new line
    opacityArea: 0.35, // The opacity of the area of the blob
    dotRadius: 4, // The size of the colored circles of each blog
    opacityCircles: 0.1, // The opacity of the circles of each blob
    strokeWidth: 2, // The width of the stroke around each blob
    roundStrokes: false, // If true, the area and stroke will follow a round path (cardinal-closed)
    color: d3.scaleOrdinal(d3.schemeCategory10), // Color function
    format: '.2%',
    unit: '', // The unit to display after the value
    ...options,
  };

  const allAxis = data[0].axes.map((i) => i.axis);
  const total = allAxis.length;
  const radius = Math.min(cfg.w / 2, cfg.h / 2);
  const angleSlice = (Math.PI * 2) / total;

  // Scale for the radius
  const maxValue = Math.max(
    cfg.maxValue,
    d3.max(data, (d) => d3.max(d.axes, (o) => o.value))
  );
  const rScale = d3.scaleLinear().range([0, radius]).domain([0, maxValue]);

  // Remove any existing SVG
  d3.select(selector).select("svg").remove();

  // Initiate the radar chart SVG
  const svg = d3
    .select(selector)
    .append("svg")
    .attr("width", cfg.w + margin.left + margin.right)
    .attr("height", cfg.h + margin.top + margin.bottom)
    .attr(
      "viewBox",
      `0 0 ${cfg.w + margin.left + margin.right} ${
        cfg.h + margin.top + margin.bottom
      }`
    )
    .append("g")
    .attr(
      "transform",
      `translate(${cfg.w / 2 + margin.left},${cfg.h / 2 + margin.top})`
    );

  // Filter for the outside glow
  const filter = svg.append("defs").append("filter").attr("id", "glow");
  filter
    .append("feGaussianBlur")
    .attr("stdDeviation", "2.5")
    .attr("result", "coloredBlur");
  const feMerge = filter.append("feMerge");
  feMerge.append("feMergeNode").attr("in", "coloredBlur");
  feMerge.append("feMergeNode").attr("in", "SourceGraphic");

  // Draw the Circular grid
  const axisGrid = svg.append("g").attr("class", "axisWrapper");

  // Draw the background circles
  axisGrid
    .selectAll(".levels")
    .data(d3.range(1, cfg.levels + 1).reverse())
    .enter()
    .append("circle")
    .attr("class", "gridCircle")
    .attr("r", (d) => (radius / cfg.levels) * d)
    .style("fill", "#CDCDCD")
    .style("stroke", "#CDCDCD")
    .style("fill-opacity", cfg.opacityCircles)
    .style("filter", "url(#glow)");

  // Text indicating at what % each level is
  axisGrid
    .selectAll(".axisLabel")
    .data(d3.range(1, cfg.levels + 1).reverse())
    .enter()
    .append("text")
    .attr("class", "axisLabel")
    .attr("x", 4)
    .attr("y", (d) => (-d * radius) / cfg.levels)
    .attr("dy", "0.4em")
    .style("font-size", "10px")
    .attr("fill", "#737373")
    .text((d) =>
      d3.format(cfg.format)((maxValue * d) / cfg.levels) + cfg.unit
    );

  // Draw the axes
  const axis = axisGrid
    .selectAll(".axis")
    .data(allAxis)
    .enter()
    .append("g")
    .attr("class", "axis");

  // Append the lines
  axis
    .append("line")
    .attr("x1", 0)
    .attr("y1", 0)
    .attr("x2", (d, i) => rScale(maxValue * 1.1) * Math.cos(angleSlice * i - Math.PI / 2))
    .attr("y2", (d, i) => rScale(maxValue * 1.1) * Math.sin(angleSlice * i - Math.PI / 2))
    .attr("class", "line")
    .style("stroke", "white")
    .style("stroke-width", "2px");

  // Append the labels at each axis
  axis
    .append("text")
    .attr("class", "legend")
    .style("font-size", "11px")
    .attr("text-anchor", "middle")
    .attr("dy", "0.35em")
    .attr("x", (d, i) =>
      rScale(maxValue * cfg.labelFactor) * Math.cos(angleSlice * i - Math.PI / 2)
    )
    .attr("y", (d, i) =>
      rScale(maxValue * cfg.labelFactor) * Math.sin(angleSlice * i - Math.PI / 2)
    )
    .text((d) => d)
    .call(wrap, cfg.wrapWidth);

  // The radial line function
  const radarLine = d3
    .lineRadial()
    .curve(d3.curveLinearClosed)
    .radius((d) => rScale(d.value))
    .angle((d, i) => i * angleSlice);

  if (cfg.roundStrokes) {
    radarLine.curve(d3.curveCardinalClosed);
  }

  // Create a wrapper for the blobs
  const blobWrapper = svg
    .selectAll(".radarWrapper")
    .data(data)
    .enter()
    .append("g")
    .attr("class", "radarWrapper");

  // Append the backgrounds
  blobWrapper
    .append("path")
    .attr("class", "radarArea")
    .attr("d", (d) => radarLine(d.axes))
    .style("fill", (d, i) => cfg.color(i))
    .style("fill-opacity", cfg.opacityArea)
    .on("mouseover", function (event, d) {
      // Dim all blobs
      d3.selectAll(".radarArea")
        .transition()
        .duration(200)
        .style("fill-opacity", 0.1);
      // Bring back the hovered blob
      d3.select(this).transition().duration(200).style("fill-opacity", 0.7);
    })
    .on("mouseout", () => {
      // Bring back all blobs
      d3.selectAll(".radarArea")
        .transition()
        .duration(200)
        .style("fill-opacity", cfg.opacityArea);
    });

  // Create the outlines
  blobWrapper
    .append("path")
    .attr("class", "radarStroke")
    .attr("d", (d) => radarLine(d.axes))
    .style("stroke-width", cfg.strokeWidth + "px")
    .style("stroke", (d, i) => cfg.color(i))
    .style("fill", "none")
    .style("filter", "url(#glow)");

  // Append the circles
  blobWrapper
    .selectAll(".radarCircle")
    .data((d) => d.axes)
    .enter()
    .append("circle")
    .attr("class", "radarCircle")
    .attr("r", cfg.dotRadius)
    .attr("cx", (d, i) =>
      rScale(d.value) * Math.cos(angleSlice * i - Math.PI / 2)
    )
    .attr("cy", (d, i) =>
      rScale(d.value) * Math.sin(angleSlice * i - Math.PI / 2)
    )
    .style("fill", (d) => cfg.color(d.id))
    .style("fill-opacity", 0.8);

  // Tooltip
  const tooltip = d3
    .select(selector)
    .append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);

  // Append invisible circles for tooltip
  const blobCircleWrapper = svg
    .selectAll(".radarCircleWrapper")
    .data(data)
    .enter()
    .append("g")
    .attr("class", "radarCircleWrapper");

  blobCircleWrapper
    .selectAll(".radarInvisibleCircle")
    .data((d) => d.axes)
    .enter()
    .append("circle")
    .attr("class", "radarInvisibleCircle")
    .attr("r", cfg.dotRadius * 1.5)
    .attr("cx", (d, i) =>
      rScale(d.value) * Math.cos(angleSlice * i - Math.PI / 2)
    )
    .attr("cy", (d, i) =>
      rScale(d.value) * Math.sin(angleSlice * i - Math.PI / 2)
    )
    .style("fill", "none")
    .style("pointer-events", "all")
    .on("mouseover", function (event, d) {
      tooltip
        .style("left", event.pageX + "px")
        .style("top", event.pageY - 28 + "px")
        .transition()
        .duration(200)
        .style("opacity", 0.9);
      tooltip.html(
        `<strong>${d.axis}</strong>: ${d3.format(cfg.format)(d.value)}${
          cfg.unit
        }`
      );
    })
    .on("mouseout", () => {
      tooltip.transition().duration(200).style("opacity", 0);
    });

  // Legend
  const legendZone = svg.append("g");
  const names = data.map((d) => d.name);
  if (typeof cfg.legend !== "undefined") {
    const legend = legendZone
      .append("g")
      .attr("class", "legend")
      .attr(
        "transform",
        `translate(${cfg.legend.translateX},${cfg.legend.translateY})`
      );
    // Create rectangles markers
    legend
      .selectAll("rect")
      .data(names)
      .enter()
      .append("rect")
      .attr("x", cfg.w / 2 - 65)
      .attr("y", (d, i) => i * 20)
      .attr("width", 10)
      .attr("height", 10)
      .style("fill", (d, i) => cfg.color(i));
    // Create labels
    legend
      .selectAll("text")
      .data(names)
      .enter()
      .append("text")
      .attr("x", cfg.w / 2 - 52)
      .attr("y", (d, i) => i * 20 + 9)
      .attr("font-size", "11px")
      .attr("fill", "#737373")
      .text((d) => d);
  }

  // Helper function to wrap long labels
  function wrap(text, width) {
    text.each(function () {
      const text = d3.select(this);
      const words = text.text().split(/\s+/).reverse();
      let word;
      let line = [];
      let lineNumber = 0;
      const lineHeight = 1.4; // ems
      const y = text.attr("y");
      const x = text.attr("x");
      const dy = parseFloat(text.attr("dy"));
      let tspan = text
        .text(null)
        .append("tspan")
        .attr("x", x)
        .attr("y", y)
        .attr("dy", dy + "em");

      while ((word = words.pop())) {
        line.push(word);
        tspan.text(line.join(" "));
        if (tspan.node().getComputedTextLength() > width) {
          line.pop();
          tspan.text(line.join(" "));
          line = [word];
          tspan = text
            .append("tspan")
            .attr("x", x)
            .attr("y", y)
            .attr("dy", ++lineNumber * lineHeight + dy + "em")
            .text(word);
        }
      }
    });
  }
}
