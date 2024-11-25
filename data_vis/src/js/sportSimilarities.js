  import {
  createDropDictFromList,
  apiCall,
  generateRandomColors,
} from "./utils.js";
import props from "./properties.js";
import {
  setUpOptions,
  setupMultiSelect,
  setupSingleSelect,
  setUpModifiableOptions,
} from "./dropDown.js";
import { createLineChart } from "./timeSeries.js";

const optionsFeatures = createDropDictFromList(
  props.Properties.filter((item) =>
    ["Height", "BMI", "Age", "GDP"].includes(item)
  )
);

const multiDropDownId = "multiDropdown";
const displayMultiContainerId = "selectedItemsList";
const toogleCheckboxId = "toggleCheckbox";
//const dropDownContainerId = "dropdown";
//const displaySingleContainerId = "selectedItemContainer1";
const radioGroupId = "sexCategory";

const { getSelectedItem: getCountry } = setupSingleSelect(
  dropDownContainerId,
  displaySingleContainerId
);

const { getSelectedItem: getSex } = setupSingleSelect(
  dropDownContainerId2,
  displaySingleContainerId2
);

const { getSelectedItems, removeAllSelectedItems } = setupMultiSelect(
  multiDropDownId,
  displayMultiContainerId
);

setUpOptions(dropDownContainerId, options);
setUpModifiableOptions(
  toogleCheckboxId,
  multiDropDownId,
  removeAllSelectedItems,
  optionsFeatures,
  optionsFeatures
);

//const {getSelectedItem} = setupSingleSelect(dropDownContainerId, displaySingleContainerId);

document
  .getElementById("dataForm")
  .addEventListener("submit", async (event) => {
    event.preventDefault(); // Prevent default form submission
    const checkBox = document.getElementById(toogleCheckboxId);
    //const sexCategory = document.getElementById(radioGroupId);
    const sexCategory = document.querySelector(
      'input[name="sexCategory"]:checked'
    );
    //console.log(sexCategory);

    // Verifica se o radio button foi selecionado
    if (!sexCategory) {
      alert("Please select a gender (Male or Female).");
      return;
    }

    const selectedSexCategory = sexCategory ? sexCategory.id : "None";
    console.log(selectedSexCategory);

    const selectedItems = getSelectedItems();
    // Se não houver itens selecionados, trata o erro
    if (selectedItems.length === 0) {
      alert("Please select at least one feature.");
      return;
    }

    const requestData = {
      agg_level: checkBox.checked ? "Event" : "Sport",
      sex: selectedSexCategory/*.toString()*/,
      features: getSelectedItems()/*.toString()*/,
    };

    try {
      // Envia os dados para o backend
      const responseData = await apiCall(
        requestData,
        "http://localhost:8000/api/getSportsDistance"
      );

      // Usar a resposta para plotar com D3

      console.log(responseData)
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
