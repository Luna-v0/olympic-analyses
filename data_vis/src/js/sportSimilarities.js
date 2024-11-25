import * as d3 from "d3";
import props from "./properties.js";
import { createDropDictFromList, apiCall } from "./utils";
import { generateTable } from './tables.js';
import { setUpOptions } from "./dropDown.js";
import { createParallelCoordinatesChart } from "./parallelCoords.js";

const optionsListForDropDown = createDropDictFromList(
  props.Properties.filter(
    (item) => !["Event", "Sport", "City", "Year", "NOC", "Team", "Games", "Medal", "BMI"].includes(item)
  )
);

setUpOptions("multiDropdown", optionsListForDropDown);

// Function to fetch available options for sports/events
function fetchSportsOrEvents(aggLevel, gender) {
  apiCall("", `http://localhost:8000/api/getNames?agg_level=${aggLevel}&gender=${gender}`)
    .then((options) => {
      const highlightSportDropdown = document.getElementById("highlightSport");
      highlightSportDropdown.innerHTML = ""; // Clear existing options
      options.forEach((sport) => {
        const option = document.createElement("option");
        option.value = sport;
        option.textContent = sport;
        highlightSportDropdown.appendChild(option);
      });
    })
    .catch((error) => console.error("Error fetching sports/events options:", error));
}

// Event listener for the aggregation level selector
document.getElementById("toggleCheckbox").addEventListener("change", () => {
  const aggLevel = document.getElementById("toggleCheckbox").checked
    ? "Event"
    : "Sport";
  const gender = document.querySelector('input[name="sexCategory"]:checked')?.id || "M";
  fetchSportsOrEvents(aggLevel, gender);
});

// Event listener for the gender selector
document.querySelectorAll('input[name="sexCategory"]').forEach((radio) => {
  radio.addEventListener("change", () => {
    const aggLevel = document.getElementById("toggleCheckbox").checked
      ? "Event"
      : "Sport";
    const gender = document.querySelector('input[name="sexCategory"]:checked').id;
    fetchSportsOrEvents(aggLevel, gender);
  });
});

// Fetch data and update the parallel coordinates chart
document.getElementById("dataForm").addEventListener("submit", async (event) => {
  event.preventDefault(); // Prevent default form submission

  const aggLevel = document.getElementById("toggleCheckbox").checked ? "Event" : "Sport";
  const gender = document.querySelector('input[name="sexCategory"]:checked');
  const highlightSport = document.getElementById("highlightSport").value;

  if (!gender) {
    alert("Please select a gender (Male or Female).");
    return;
  }

  if (!highlightSport) {
    alert("Please select a sport or event to highlight.");
    return;
  }

  const selectedItems = Array.from(document.getElementById("multiDropdown").selectedOptions).map(
    (opt) => opt.value
  );

  if (selectedItems.length === 0) {
    alert("Please select at least one feature.");
    return;
  }

  try {
    // Construct query string for features
    const featuresQuery = selectedItems.map(feature => `features=${encodeURIComponent(feature)}`).join('&');

    // Construct the full URL with query parameters
    const distancesUrl = `http://localhost:8000/api/getSportsDistance?agg_level=${encodeURIComponent(aggLevel)}&sex=${encodeURIComponent(gender.id)}&${featuresQuery}`;

    // Fetch distances between sports/events
    const distances = await apiCall("", distancesUrl);

    // Fetch data for the parallel coordinates chart using the correct endpoint
    const chartDataRequestData = {
      eventOrSport: aggLevel,
      gender: gender.id,
      features: selectedItems,
    };
    const chartData = await apiCall(
      chartDataRequestData,
      "http://localhost:8000/api/getSportsToCompareWithUser"
    );
    let highlightedSportRow;
    // Find the row for the highlighted sport
    if(aggLevel === "Sport"){
        highlightedSportRow = chartData.find((row) => row.Sport === highlightSport);
    }
    else{
        highlightedSportRow = chartData.find((row) => row.Event === highlightSport);
    }

    if (!highlightedSportRow) {
      console.error("Highlighted sport not found in chart data.");
      alert("The highlighted sport was not found in the data.");
      return;
    }

    // Normalize data and calculate opacity based on distance to highlighted sport/event
    const indexColumn = aggLevel === "Event" ? "Event" : "Sport";
    const highlightedDistances = distances.filter(
      (d) => d[`${indexColumn}_1`] === highlightSport || d[`${indexColumn}_2`] === highlightSport
    );

    const maxDistance = Math.max(...highlightedDistances.map((d) => d.Distance));
    const minDistance = Math.min(...highlightedDistances.map((d) => d.Distance));

    chartData.forEach((item) => {
      const distanceObj = highlightedDistances.find(
        (d) =>
          (d[`${indexColumn}_1`] === item.Name && d[`${indexColumn}_2`] === highlightSport) ||
          (d[`${indexColumn}_2`] === item.Name && d[`${indexColumn}_1`] === highlightSport)
      );

      if (distanceObj) {
        const normalizedDistance = (distanceObj.Distance - minDistance) / (maxDistance - minDistance);
        const alpha = 5;
        item.opacity = (Math.exp(alpha * (1 - normalizedDistance)) - 1) / (Math.exp(alpha) - 1);
      } else if (item.Name === highlightSport) {
        item.opacity = 1.0; // Highlighted sport/event has maximum opacity
      } else {
        item.opacity = 0.1; // Default minimal opacity for others not found in distances
      }
    });

    // Create the parallel coordinates chart
    createParallelCoordinatesChart("parallelCoords", chartData, selectedItems, highlightedSportRow, aggLevel);

  } catch (error) {
    console.error("Error fetching data:", error);
    alert("An error occurred while fetching the data.");
  }
});

// Initial population of the dropdown
fetchSportsOrEvents("Sport", "M");
