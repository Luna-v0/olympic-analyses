import props from "./properties";
import { setUpOptions, setupSingleSelect } from "./dropDown";
import { createDropDictFromList, apiCall } from "./utils";
import { generateTable } from "./tables";
import { createParallelCoordinatesChart } from "./parallelCoords";

const options = createDropDictFromList(props.NOC);
const sexOptions = createDropDictFromList(["M", "F"]);

const dropDownContainerId = "dropdown";
const displaySingleContainerId = "selectedItemContainer1";
const dropDownContainerId2 = "dropdown2";
const displaySingleContainerId2 = "selectedItemContainer2";

setUpOptions(dropDownContainerId, options);
setUpOptions(dropDownContainerId2, sexOptions);

const { getSelectedItem: getCountry } = setupSingleSelect(
  dropDownContainerId,
  displaySingleContainerId
);

const { getSelectedItem: getSex } = setupSingleSelect(
  dropDownContainerId2,
  displaySingleContainerId2
);

document
  .getElementById("dataForm")
  .addEventListener("submit", async (event) => {
    event.preventDefault(); // Prevent default form submission

    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    const userData = {
      NOC: getCountry(),
      Age: Number(data.Age),
      Height: Number(data.Height),
      Weight: Number(data.Weight),
      Sex: getSex(),
    }


    const requestData = {
      _user_data: JSON.stringify(userData),
      agg_level: "Sport",
    };

    try {
      // Send data to backend
      const [responseTableData, user_gdp] = await apiCall(
        requestData,
        "http://localhost:8000/api/getSportsForUser"
      );

      const responseChartData = await apiCall(
        {eventOrSport: "Sport", gender: userData.Sex},
        "http://localhost:8000/api/getSportsToCompareWithUser"
      );
      userData.GDP = user_gdp;

      const alpha = 5;
      const maxDistance = Math.max(...responseTableData.map((row) => row.Distance));
      const minDistance = Math.min(...responseTableData.map((row) => row.Distance));
      responseTableData.forEach((row) => {
        responseChartData.forEach((sport) => {
          console.log(row.Sport, sport.Sport);
          if (row.Sport === sport.Sport) {
            const normalized = (row.Distance - minDistance) / (maxDistance - minDistance);
            sport.opacity = (Math.exp(alpha * normalized) - 1) / (Math.exp(alpha) - 1)
          }
        });
      });

      createParallelCoordinatesChart("parallelCoords", responseChartData,[
        "Age",
        "Height",
        "Weight",
        "NOC",
        "GDP"
      ], userData, "Sport");
      generateTable("rankingTable", responseTableData);
    } catch (error) {
      console.error("Error fetching data:", error);
      alert("An error occurred. Please try again.");
    }
  });
