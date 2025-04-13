document.getElementById("predictForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const payload = {
    avg_speed: parseFloat(document.getElementById("avg_speed").value),
    distance: parseFloat(document.getElementById("distance").value),
    battery: parseFloat(document.getElementById("battery").value),
    top_speed: parseFloat(document.getElementById("top_speed").value),
    passenger: parseFloat(document.getElementById("passenger").value),
    road_type: document.getElementById("road_type").value,
    bus_type: document.getElementById("bus_type").value,
    charger_type: document.getElementById("charger_type").value,
  };

  // Show loader and hide result initially
  document.getElementById("loader").style.display = "block";
  document.getElementById("result").style.display = "none";

  try {
    const response = await fetch("http://localhost:5000/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const result = await response.json();
    document.getElementById("loader").style.display = "none";

    if (result.error) {
      document.getElementById("result").textContent = `Error: ${result.error}`;
      return;
    }

    // Display prediction result
    document.getElementById("result").style.display = "block";
    document.getElementById("result").innerHTML =
      `🔋 <strong>${result.efficiency}</strong> battery<br>` +
      `📏 Predicted Range: <strong>${result.predicted_range} km</strong><br>` +
      `📊 Efficiency: <strong>${result.efficiency_percent}%</strong>`;

    // Draw Bar Chart using Chart.js
    const ctx = document.getElementById("rangeChart").getContext("2d");
    if (window.rangeChart && typeof window.rangeChart.destroy === 'function') {
      window.rangeChart.destroy();
    }
    window.rangeChart = new Chart(ctx, {
      type: "bar",
      data: {
        labels: ["Predicted Range (km)"],
        datasets: [{
          label: result.efficiency,
          data: [result.predicted_range],
          backgroundColor:
            result.efficiency === "Efficient" ? "#00e676" :
            result.efficiency === "Moderate" ? "#ffca28" : "#ef5350"
        }]
      },
      options: {
        scales: {
          y: {
            beginAtZero: true,
            max: 400,
            ticks: { color: "#fff" },
            grid: { color: "#333" }
          },
          x: {
            ticks: { color: "#fff" },
            grid: { color: "#333" }
          }
        },
        plugins: { legend: { labels: { color: "#fff" } } }
      }
    });

    // Draw Pie Chart for efficiency percentage
    const ptx = document.getElementById("pieChart").getContext("2d");
    if (window.pieChart && typeof window.pieChart.destroy === "function") {
      window.pieChart.destroy();
    }
    window.pieChart = new Chart(ptx, {
      type: "pie",
      data: {
        labels: ["Efficiency %", "Remaining %"],
        datasets: [{
          data: [result.efficiency_percent, 100 - result.efficiency_percent],
          backgroundColor: ["#03a9f4", "#eeeeee"]
        }]
      },
      options: {
        plugins: { legend: { labels: { color: "#fff" } } }
      }
    });

    // If efficiency_percent >= 90, prompt for upload to website
    if (result.efficiency_percent >= 90) {
      window.latestPrediction = result;
      document.getElementById("uploadModal").style.display = "block";
    }

  } catch (error) {
    document.getElementById("loader").style.display = "none";
    document.getElementById("result").textContent = "Error while fetching prediction.";
    console.error("Fetch error:", error);
  }
});

// Upload modal logic
document.getElementById("uploadForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  // Use correct keys: company_name and battery_model as per your backend
  const data = {
    ...window.latestPrediction,
    company_name: document.getElementById("company").value,
    battery_model: document.getElementById("model_id").value,
    year: document.getElementById("year").value
  };

  try {
    await fetch("http://localhost:5000/upload", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });

    alert("✅ Uploaded successfully!");
    closeModal();
  } catch (err) {
    alert("❌ Upload failed.");
    console.error(err);
  }
});

function closeModal() {
  document.getElementById("uploadModal").style.display = "none";
}
