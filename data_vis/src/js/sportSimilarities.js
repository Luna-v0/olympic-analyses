import { createDropDictFromList, apiCall, generateRandomColors } from "./utils.js";
import props from "./properties.js";
import { setUpOptions, setupMultiSelect, setupSingleSelect, setUpModifiableOptions } from "./dropDown.js";
import { createLineChart } from "./timeSeries.js";

const optionsEvent = createDropDictFromList(props.Event);
const optionsSport = createDropDictFromList(props.Sport);

const optionsListForSingleDropDown = createDropDictFromList(
  props.Properties.filter(
    (item) => !["Event", "Sport", "City","Year"].includes(item)
  )
);

const multiDropDownId = "multiDropdown";
const displayMultiContainerId = "selectedItemsList";
const toogleCheckboxId = "toggleCheckbox";
const dropDownContainerId = "dropdown";
const displaySingleContainerId = "selectedItemContainer1";

const { getSelectedItems, removeAllSelectedItems } = setupMultiSelect(
  multiDropDownId,
  displayMultiContainerId
);

setUpOptions(dropDownContainerId, optionsListForSingleDropDown);
setUpModifiableOptions(toogleCheckboxId,multiDropDownId, removeAllSelectedItems, optionsEvent, optionsSport);


const {getSelectedItem} = setupSingleSelect(dropDownContainerId, displaySingleContainerId);

document
  .getElementById("dataForm")
  .addEventListener("submit", async (event) => {
    event.preventDefault(); // Prevent default form submission
    const checkBox = document.getElementById(toogleCheckboxId);


    const requestData = {
      isSportsOrEvents: checkBox.checked ? "sport" : "event",
      feature: getSelectedItem(),
      sportsOrEvents: getSelectedItems(),
    };

    try {
      // Send data to backend
      const responseData = await apiCall(
        requestData,
        "http://localhost:8000/api/timeTendencies"
      );

      // Use response data for D3 plotting
      createLineChart({
        selector: "#timeSeries",
        data: responseData,
        lineColors: generateRandomColors(responseData),
      });
    } catch (error) {
      console.error("Error fetching data:", error);
      alert("An error occurred. Please try again.");
    }
  });
