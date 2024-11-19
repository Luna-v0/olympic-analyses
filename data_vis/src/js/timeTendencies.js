import { createDropDictFromList, apiCall, generateRandomColors } from "./utils";
import props from "./properties.js";
import { setUpOptions, setupMultiSelect } from "./multiDropDown";
import { createLineChart } from "./timeSeries";

const optionsList = createDropDictFromList(props.Event);

const multiDropDownId = "multiDropdown";
const displayContainerId = "selectedItemsList";

setUpOptions(multiDropDownId, optionsList);

const { getSelectedItems } = setupMultiSelect(
  multiDropDownId,
  displayContainerId
);



document
  .getElementById("dataForm")
  .addEventListener("submit", async (event) => {
    event.preventDefault(); // Prevent default form submission

    // Gather form data
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());

    try {
      // Send data to backend
      const responseData = await apiCall({ data: ["1"] }, "http://localhost:8000/api/timeTendencies")

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
