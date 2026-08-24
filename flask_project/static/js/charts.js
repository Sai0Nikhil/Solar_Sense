// SolarSense Chart.js Integration Engine (Soft Light Skin Tone Theme)
document.addEventListener("DOMContentLoaded", () => {
  if (!window.SOLAR_DATA) return;
  const D = window.SOLAR_DATA;

  // 1. Distribution Histograms
  if (D.histograms) {
    document.querySelectorAll("[data-chart='hist']").forEach(canvas => {
      const key = canvas.getAttribute("data-key");
      const h = D.histograms[key];
      if (!h || !h.labels) return;

      new Chart(canvas, {
        type: "bar",
        data: {
          labels: h.labels,
          datasets: [{
            data: h.counts,
            backgroundColor: "rgba(200, 122, 40, 0.75)",
            hoverBackgroundColor: "#C87A28",
            borderRadius: 3
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { grid: { display: false }, ticks: { color: "#6E5542", font: { size: 10 } } },
            y: { grid: { color: "#E8DCcc" }, ticks: { color: "#6E5542", font: { size: 10 } } }
          }
        }
      });
    });
  }

  // 2. Standardized Z-Score Charts
  if (D.standardized) {
    document.querySelectorAll("[data-chart='std']").forEach(canvas => {
      const key = canvas.getAttribute("data-key");
      const h = D.standardized[key];
      if (!h || !h.labels) return;

      new Chart(canvas, {
        type: "bar",
        data: {
          labels: h.labels,
          datasets: [{
            data: h.counts,
            backgroundColor: "rgba(75, 114, 134, 0.75)",
            hoverBackgroundColor: "#4B7286",
            borderRadius: 3
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { grid: { display: false }, ticks: { color: "#6E5542", font: { size: 10 } } },
            y: { grid: { color: "#E8DCcc" }, ticks: { color: "#6E5542", font: { size: 10 } } }
          }
        }
      });
    });
  }

  // 3. Imputation Strategy Benchmark Chart
  const impBenchCanvas = document.querySelector("[data-chart='imputation_benchmark']");
  if (impBenchCanvas && D.imputation_lab) {
    const lab = D.imputation_lab;
    new Chart(impBenchCanvas, {
      type: "bar",
      data: {
        labels: lab.chart_labels,
        datasets: [
          {
            label: "Forward Fill (LOCF)",
            data: lab.chart_ffill_rmse,
            backgroundColor: "rgba(194, 62, 52, 0.75)",
            borderRadius: 4
          },
          {
            label: "Diurnal Pattern",
            data: lab.chart_diurnal_rmse,
            backgroundColor: "rgba(75, 114, 134, 0.75)",
            borderRadius: 4
          },
          {
            label: "Time Linear Spline (Winner)",
            data: lab.chart_linear_rmse,
            backgroundColor: "#C87A28",
            borderRadius: 4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: "#2C1E14", font: { family: "Inter", size: 11, weight: "600" } } },
          title: { display: true, text: "Imputation Reconstruction Error (RMSE - Lower is Better)", color: "#2C1E14" }
        },
        scales: {
          x: { grid: { color: "#E8DCcc" }, ticks: { color: "#2C1E14", font: { weight: "600" } } },
          y: {
            grid: { color: "#E8DCcc" },
            ticks: { color: "#6E5542" },
            title: { display: true, text: "Root Mean Squared Error (RMSE)", color: "#6E5542" }
          }
        }
      }
    });
  }

  // 4. Influence on AC Power Horizontal Bar Chart
  const inflCanvas = document.querySelector("[data-chart='influence']");
  if (inflCanvas && D.influence) {
    new Chart(inflCanvas, {
      type: "bar",
      data: {
        labels: D.influence.labels,
        datasets: [{
          data: D.influence.values,
          backgroundColor: D.influence.values.map(v => v >= 0 ? "#C87A28" : "#C23E34"),
          borderRadius: 4
        }]
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: "#E8DCcc" }, ticks: { color: "#6E5542" } },
          y: { grid: { display: false }, ticks: { color: "#2C1E14", font: { weight: "600" } } }
        }
      }
    });
  }

  // 5. Diurnal Power vs Irradiance Dual-Axis Line Chart
  const diurnalCanvas = document.querySelector("[data-chart='diurnal']");
  if (diurnalCanvas && D.diurnal) {
    const d = D.diurnal;
    new Chart(diurnalCanvas, {
      type: "line",
      data: {
        labels: d.hours.map(h => `${h}:00`),
        datasets: [
          {
            label: "AC Power (kW)",
            data: d.ac_power,
            borderColor: "#C87A28",
            backgroundColor: "rgba(200, 122, 40, 0.12)",
            fill: true,
            tension: 0.35,
            yAxisID: "y"
          },
          {
            label: "Solar Irradiance (W/m²)",
            data: d.irradiation,
            borderColor: "#4B7286",
            borderDash: [5, 5],
            tension: 0.35,
            yAxisID: "y1"
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: "#2C1E14", font: { family: "Inter", size: 11, weight: "600" } } }
        },
        scales: {
          x: { grid: { color: "#E8DCcc" }, ticks: { color: "#6E5542" } },
          y: {
            title: { display: true, text: "Power (kW)", color: "#C87A28" },
            grid: { color: "#E8DCcc" },
            ticks: { color: "#6E5542" }
          },
          y1: {
            position: "right",
            title: { display: true, text: "Irradiance (W/m²)", color: "#4B7286" },
            grid: { display: false },
            ticks: { color: "#4B7286" }
          }
        }
      }
    });
  }

  // 6. Feature Importance Chart
  const impCanvas = document.querySelector("[data-chart='importance']");
  if (impCanvas && D.importance) {
    new Chart(impCanvas, {
      type: "bar",
      data: {
        labels: D.importance.labels,
        datasets: [{
          label: "Relative Gini Importance",
          data: D.importance.values,
          backgroundColor: "#C87A28",
          borderRadius: 4
        }]
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: "#E8DCcc" }, ticks: { color: "#6E5542" } },
          y: { grid: { display: false }, ticks: { color: "#2C1E14", font: { weight: "600" } } }
        }
      }
    });
  }
});
