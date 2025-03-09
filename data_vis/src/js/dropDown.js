/**
 * Sets up a multi-select with dynamic display and removal of selected items.
 * @param {string} dropdownId - The ID of the <select> element (dropdown).
 * @param {string} displayContainerId - The ID of the container to display selected items.
 * @returns {object} - An object with methods to get the selected items.
 */
export function setupMultiSelect(dropdownId, displayContainerId) {
  // Reference elements
  const dropdown = document.getElementById(dropdownId);
  const displayContainer = document.getElementById(displayContainerId);

  // Track selected items
  const selectedItems = new Set();

  // Function to display selected items
  function displaySelectedItems() {
    displayContainer.innerHTML = ""; // Clear the container before updating

    selectedItems.forEach((value) => {
      const listItem = document.createElement("div");
      listItem.textContent = value;
      listItem.className =
        "p-2 bg-blue-100 text-blue-800 rounded-md cursor-pointer hover:bg-blue-200";
      listItem.dataset.value = value; // Store the value for easy removal

      // Add click event to remove item
      listItem.addEventListener("click", () => {
        removeSelectedItem(value);
      });

      displayContainer.appendChild(listItem);
    });
  }

  // Function to add an item (double-click)
  function addSelectedItem(value) {
    if (!selectedItems.has(value)) {
      selectedItems.add(value); // Add to Set
      displaySelectedItems(); // Refresh the displayed list
    }
  }

  // Function to remove an item (single-click)
  function removeSelectedItem(value) {
    selectedItems.delete(value); // Remove from Set
    displaySelectedItems(); // Refresh the displayed list
  }

  // Event listener for double-clicking dropdown options
  dropdown.addEventListener("dblclick", (event) => {
    const selectedOption = event.target;
    if (selectedOption && selectedOption.tagName === "OPTION") {
      addSelectedItem(selectedOption.value);
    }
  });

  function removeAllSelectedItems() {
    selectedItems.clear(); // Clear all selected items
    displaySelectedItems(); // Refresh the displayed list
  }

  // Expose a method to get the selected items
  return {
    getSelectedItems: () => Array.from(selectedItems), // Return selected items as an array
    removeAllSelectedItems: () => removeAllSelectedItems(),
    addSelectedItem: (item) => addSelectedItem(item)
  };
}

export function setUpOptions(dropdownId, optionsList) {
  const multiDropdown = document.getElementById(dropdownId);
  multiDropdown.innerHTML = '';

  // Populate the dropdown with options
  optionsList.forEach((option) => {
    const opt = document.createElement("option");
    opt.value = option.value;
    opt.textContent = option.label;
    multiDropdown.appendChild(opt);
  });
}

export function setUpModifiableOptions(checkbox, dropdownId, clear, arr1,arr2) {
  const checkBox = document.getElementById(checkbox);
  const whichArr = (checked) => checked ? arr1 : arr2;


  setUpOptions(dropdownId, whichArr(checkBox.checked));

  checkBox.addEventListener('change', (event) => {
    clear();
    setUpOptions(dropdownId, whichArr(event.target.checked));
  });
}

/**
 * Sets up a single-select dropdown with dynamic display and removal of the selected item.
 * @param {string} dropdownId - The ID of the <select> element (dropdown).
 * @param {string} displayContainerId - The ID of the container to display the selected item.
 * @returns {object} - An object with methods to get the selected item.
 */
export function setupSingleSelect(dropdownId, displayContainerId) {
  // Reference elements
  const dropdown = document.getElementById(dropdownId);
  const displayContainer = document.getElementById(displayContainerId);

  // Track the selected item
  let selectedItem = null;

  // Function to display the selected item
  function displaySelectedItem() {
    displayContainer.innerHTML = ''; // Clear the container before updating

    if (selectedItem) {
      const itemDiv = document.createElement('div');
      itemDiv.textContent = selectedItem;
      itemDiv.className =
        'p-2 bg-blue-100 text-blue-800 rounded-md cursor-pointer hover:bg-blue-200';
      itemDiv.dataset.value = selectedItem; // Store the value for easy removal

      // Add click event to remove the item
      itemDiv.addEventListener('click', () => {
        removeSelectedItem();
      });

      displayContainer.appendChild(itemDiv);
    }
  }

  // Function to set the selected item
  function setSelectedItem(value) {
    selectedItem = value;
    displaySelectedItem();
  }

  // Function to remove the selected item
  function removeSelectedItem() {
    selectedItem = null; // Clear the selected item
    displayContainer.innerHTML = ''; // Clear the display container
  }

  // Event listener for selecting an option
  dropdown.addEventListener('change', (event) => {
    const selectedOption = event.target.value;
    setSelectedItem(selectedOption);
  });


  // Expose a method to get the selected item
  return {
    getSelectedItem: () => selectedItem,
    removeSelectedItem: () => removeSelectedItem(),
    setSelectedItem: (item) => setSelectedItem(item)
  };
}