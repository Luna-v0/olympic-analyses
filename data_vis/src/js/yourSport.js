import props from "./properties";
import { setUpOptions, setupSingleSelect } from "./dropDown";
import { createDropDictFromList, apiCall } from "./utils";
import { generateTable } from "./tables";

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

    const requestData = {
      _user_data: JSON.stringify({
        NOC: getCountry(),
        Age: Number(data.Age),
        Height: Number(data.Height),
        Weight: Number(data.Weight),
        Sex: getSex(),
      }),
      agg_level: "Sport",
    };

    try {
      // Send data to backend
      const responseData = await apiCall(
        requestData,
        "http://localhost:8000/api/getSportsForUser"
      );

      generateTable("rankingTable", responseData);
    } catch (error) {
      console.error("Error fetching data:", error);
      alert("An error occurred. Please try again.");
    }
  });
