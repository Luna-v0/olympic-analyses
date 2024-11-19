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

  // Expose a method to get the selected items
  return {
    getSelectedItems: () => Array.from(selectedItems), // Return selected items as an array
  };
}

export function setUpOptions(dropdownId, optionsList) {
  const multiDropdown = document.getElementById(dropdownId);

  // Populate the dropdown with options
  optionsList.forEach((option) => {
    const opt = document.createElement("option");
    opt.value = option.value;
    opt.textContent = option.label;
    multiDropdown.appendChild(opt);
  });
}