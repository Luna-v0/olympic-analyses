import props from "./properties";
import { setUpOptions, setupSingleSelect, setupMultiSelect } from "./dropDown";
import { createDropDictFromList, apiCall } from "./utils";
import { generateTable } from "./tables";
import { createParallelCoordinatesChart } from "./parallelCoords";

const backOptions = [ "Age", "Height", "BMI", "GDP"]

const options = createDropDictFromList(
  props.Properties.filter((item) => backOptions.includes(item))
);
const sexOptions = createDropDictFromList(["M", "F"]);

const dropDownContainerId = "multiDropdown";
const displaySingleContainerId = "selectedItemsContainer";
const dropDownContainerId2 = "dropdown2";
const displaySingleContainerId2 = "selectedItemContainer2";

setUpOptions(dropDownContainerId, options);
setUpOptions(dropDownContainerId2, sexOptions);

const { getSelectedItems: getFeatures } = setupMultiSelect(
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
    console.log(getFeatures());

    const requestData = {
      agg_level: "Sport",
      sex: getSex(),
      features: getFeatures(),
    };

    try {
      // Send data to backend
      const responseTableData = await apiCall(
        requestData,
        "http://localhost:8000/api/getSportsDistance"
      );

      generateTable("rankingTable", responseTableData);
    } catch (error) {
      console.error("Error fetching data:", error);
      alert("An error occurred. Please try again.");
    }
  });
