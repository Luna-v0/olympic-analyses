import { createDropDictFromList, apiCall, generateRandomColors } from "./utils";
import props from "./properties.js";
import { setUpOptions, setupMultiSelect, setupSingleSelect, setUpModifiableOptions } from "./dropDown";
import { createLineChart } from "./timeSeries";

const optionsEvent = createDropDictFromList([...props.Event].sort());
const optionsSport = createDropDictFromList([...props.Sport].sort());

const optionsListForSingleDropDown = createDropDictFromList(
  props.Properties.filter(
    (item) => !["Event", "Sport", "City","Year", "NOC", "Team", "Games", "Medal"].includes(item)
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
  isSportsOrEvents: checkBox.checked ? "events" : "sports",
  feature: getSelectedItem(),
  sportsOrEvents: getSelectedItems(),
};

// Construct URL with query parameters
const baseUrl = "http://localhost:8000/api/timeTendencies";
const urlWithParams = new URL(baseUrl);
urlWithParams.searchParams.append("isSportsOrEvents", requestData.isSportsOrEvents);
urlWithParams.searchParams.append("feature", requestData.feature);

// Assuming sportsOrEvents is an array, append each item
requestData.sportsOrEvents.forEach((item) => {
  urlWithParams.searchParams.append("sportsOrEvents", item);
});

try {
  console.log("Request URL:", urlWithParams.toString());
  const responseData = await apiCall("", urlWithParams.toString()); // Empty body since parameters are in the URL

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
