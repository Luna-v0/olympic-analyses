document
  .getElementById("dataForm")
  .addEventListener("submit", async (event) => {
    event.preventDefault();

    const checkBox = document.getElementById("toggleCheckbox");
    const sexCategory = document.querySelector(
      'input[name="sexCategory"]:checked'
    );

    // Verificar seleção do gênero
    if (!sexCategory) {
      alert("Please select a gender (Male or Female).");
      return;
    }

    const selectedSexCategory = sexCategory ? sexCategory.id : "None";
    console.log(selectedSexCategory);

    // Captura os valores dos campos estáticos
    const requestData = {
      agg_level: checkBox.checked ? "event" : "sport",
      sex: selectedSexCategory,
      age: parseInt(document.getElementById("age").value),
      height: parseFloat(document.getElementById("height").value),
      weight: parseFloat(document.getElementById("weight").value),
      noc: document.getElementById("noc").value,
    };

    // Validações adicionais (opcional)
    if (
      !requestData.noc ||
      isNaN(requestData.age) ||
      isNaN(requestData.height) ||
      isNaN(requestData.weight)
    ) {
      alert("Please fill all fields correctly.");
      return;
    }

    try {
      const responseData = await apiCall(
        requestData,
        "http://localhost:8000/api/getSportsDistance"
      );

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
