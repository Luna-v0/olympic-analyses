// main.js
import * as d3 from "d3";
import { createRadarChart } from "./radarChart.js";
import { apiCall } from "./utils.js"; // Assuming you have an apiCall function

// Fetch data from your FastAPI endpoint
apiCall(
    "",
  "http://localhost:8000/api/fairestSports"
)
  .then((data) => {
    console.log("Data: " + data); // Debugging line
    // Process data to fit radar chart format
    const radarData = data.map((d) => ({
      name: d.Sport,
      axes: Object.keys(d)
        .filter((key) => key !== "Sport" && key !== "total")
        .map((key) => ({
          axis: key,
          value: d[key],
        })),
    }));

    // Set the maximum value for scaling
    const maxValue = d3.max(radarData, (d) =>
      d3.max(d.axes, (o) => o.value)
    );

    // Draw the radar chart
    createRadarChart({
      selector: "#radarChart",
      data: radarData,
      options: {
        w: 500,
        h: 500,
        maxValue: maxValue,
        levels: 5,
        roundStrokes: false,
        color: d3.scaleOrdinal().range(d3.schemeCategory10),
        format: '.2f', // Adjust format as needed
        unit: '',      // Add unit if applicable
        legend: {
          translateX: -50,
          translateY: -50,
        },
      },
    });
  })
  .catch((error) => console.error("Error fetching data:", error));
