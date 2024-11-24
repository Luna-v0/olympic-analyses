/**
 * Generates a dynamic table from data and appends it to a container.
 * @param {string} containerId - The ID of the container to append the table.
 * @param {Array<Object>} data - The array of objects representing table rows.
 * @param {Array<string>} columns - The array of column names to display.
 */
export function generateTable(containerId, data, columns=Object.keys(data[0])) {
    const container = document.getElementById(containerId);

  
    // Clear previous content
    container.innerHTML = '';
  
    // Create the table
    const table = document.createElement('table');
    table.className = 'min-w-full border-collapse border border-gray-300';
 
    // Create the table header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    headerRow.className = 'bg-gray-200';

    columns.forEach(column => {
      const th = document.createElement('th');
      th.textContent = column;
      th.className = 'border border-gray-300 p-2 text-left font-medium';
      headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);
  
    // Create the table body
    const tbody = document.createElement('tbody');
  
    data.forEach(row => {
      const tr = document.createElement('tr');
      tr.className = 'hover:bg-gray-100';

      columns.forEach(column => {
        const td = document.createElement('td');
        td.textContent = row[column] || ''; // Use empty string if value is undefined
        td.className = 'border border-gray-300 p-2';
        tr.appendChild(td);
      });
  
      tbody.appendChild(tr);
    });
  
    table.appendChild(tbody);
  
    // Append the table to the container
    container.appendChild(table);
  }
  
      tbody.appendChild(tr);
    });

    table.appendChild(tbody);

    // Append the table to the container
    container.appendChild(table);
  }
