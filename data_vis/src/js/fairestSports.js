import * as d3 from "d3";
import { createRadarChart } from "./radarChart.js";
import { apiCall } from "./utils.js";

// Function to fetch available options for the names selector
function fetchOptions(aggLevel, gender) {
  apiCall("", `http://localhost:8000/api/getNames?agg_level=${aggLevel}&gender=${gender}`)
    .then((options) => {
      const namesSelect = document.getElementById("names");
      namesSelect.innerHTML = ""; // Clear existing options
      options.forEach((opt) => {
        const option = document.createElement("option");
        option.value = opt;
        option.textContent = opt;
        namesSelect.appendChild(option);
      });
    })
    .catch((error) => console.error("Error fetching options:", error));
}
// Event listener for the aggregation level selector
document.getElementById("aggLevel").addEventListener("change", () => {
  const aggLevel = document.getElementById("aggLevel").value;
  const gender = document.getElementById("gender").value;
  fetchOptions(aggLevel, gender);
});

// Event listener for the gender selector
document.getElementById("gender").addEventListener("change", () => {
  const aggLevel = document.getElementById("aggLevel").value;
  const gender = document.getElementById("gender").value;
  fetchOptions(aggLevel, gender);
});

// Fetch data and update the radar chart
document.getElementById("fetchData").addEventListener("click", () => {
  const aggLevel = document.getElementById("aggLevel").value;
  const names = Array.from(document.getElementById("names").selectedOptions).map(
    (opt) => opt.value
  );
  const gender = document.getElementById("gender").value;
  const namesQuery = names.map(name => `names=${encodeURIComponent(name)}`).join("&");
  const url = `http://localhost:8000/api/fairestSports?agg_level=${encodeURIComponent(aggLevel)}&${namesQuery}&gender=${encodeURIComponent(gender)}`;

  // Fetch data and update the radar chart
  apiCall("", url)
    .then((data) => {
      // Process data to fit radar chart format
      const radarData = data.map((d) => ({
        name: d.Name,
        axes: Object.keys(d)
          .filter((key) => key !== "Name" && key !== "total")
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
          maxValue: 1.0,
          levels: 5,
          roundStrokes: true,
          color: d3.scaleOrdinal().range(d3.schemeCategory10), // Add color back
          format: ".2f",
          unit: "",
          legend: {
            translateX: -50,
            translateY: -50,
          },
        },
      });
    })
    .catch((error) => console.error("Error fetching data:", error));
});

// Initial fetch for default aggregation level
fetchOptions("Sport", "M");
