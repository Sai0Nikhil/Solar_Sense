/**
 * SolarSense Chart Builders
 * Built on Chart.js 4.4.3 (loaded by base.html)
 *
 * All charts are driven by window.SOLAR_DATA injected by each Jinja template.
 * Canvas elements use data-chart="<type>" to identify which builder to call.
 */

/* ------------------------------------------------------------------ Palette */
const PALETTE = {
  amber:      "rgba(217, 166, 63,  1.00)",
  amberLight: "rgba(217, 166, 63,  0.22)",
  amberMid:   "rgba(217, 166, 63,  0.55)",
  red:        "rgba(198,  93, 85,  0.85)",
  redLight:   "rgba(198,  93, 85,  0.18)",
  blue:       "rgba( 90, 152, 212, 0.85)",
  blueLight:  "rgba( 90, 152, 212, 0.20)",
  green:      "rgba( 93, 188, 130, 0.85)",
  greenLight: "rgba( 93, 188, 130, 0.18)",
  text:       getComputedStyle(document.documentElement).getPropertyValue("--text").trim()   || "#e8e3d8",
  text2:      getComputedStyle(document.documentElement).getPropertyValue("--text-2").trim() || "#9b9488",
  border:     getComputedStyle(document.documentElement).getPropertyValue("--border").trim() || "#2a2820",
};

/* ------------------------------------------------------------------ Defaults */
Chart.defaults.color            = PALETTE.text2;
Chart.defaults.font.family      = "Inter, sans-serif";
Chart.defaults.font.size        = 11;
Chart.defaults.plugins.legend.display = false;
Chart.defaults.animation        = { duration: 450, easing: "easeOutQuart" };

function gridOpts() {
  return {
    color: PALETTE.border,
    lineWidth: 0.6,
  };
}

function tickOpts(extra) {
  return Object.assign({ color: PALETTE.text2, font: { size: 10 } }, extra || {});
}

/* ================================================================== BUILDERS */

/* ---- Histogram (distributions & z-score) ---- */
function buildHist(canvas, data, color) {
  if (!data || !data.labels || !data.labels.length) return;
  new Chart(canvas, {
    type: "bar",
    data: {
      labels: data.labels,
      datasets: [{
        data: data.counts,
        backgroundColor: color || PALETTE.amberLight,
        borderColor:     color ? color.replace("0.22", "0.9") : PALETTE.amber,
        borderWidth: 1.2,
        borderRadius: 2,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { tooltip: { callbacks: { title: (i) => i[0].label } } },
      scales: {
        x: { grid: gridOpts(), ticks: tickOpts({ maxRotation: 40, font: { size: 9 } }) },
        y: { grid: gridOpts(), ticks: tickOpts(), beginAtZero: true }
      }
    }
  });
}

/* ---- Influence / Correlation Bar ---- */
function buildInfluence(canvas, data) {
  if (!data || !data.labels) return;
  const colors = data.values.map(v => v >= 0 ? PALETTE.amberMid : PALETTE.redLight);
  const borders = data.values.map(v => v >= 0 ? PALETTE.amber : PALETTE.red);
  new Chart(canvas, {
    type: "bar",
    data: {
      labels: data.labels,
      datasets: [{ data: data.values, backgroundColor: colors, borderColor: borders, borderWidth: 1.5, borderRadius: 3 }]
    },
    options: {
      indexAxis: "y",
      responsive: true, maintainAspectRatio: false,
      plugins: {
        tooltip: { callbacks: { label: (i) => `  r = ${i.raw.toFixed(3)}` } }
      },
      scales: {
        x: { grid: gridOpts(), ticks: tickOpts(), min: -1, max: 1 },
        y: { grid: { display: false }, ticks: tickOpts({ font: { size: 10 } }) }
      }
    }
  });
}

/* ---- Imputation Benchmark Grouped Bar ---- */
function buildImputationBenchmark(canvas, data) {
  if (!data) return;
  new Chart(canvas, {
    type: "bar",
    data: {
      labels: data.chart_labels,
      datasets: [
        { label: "Forward Fill",     data: data.chart_ffill_rmse,   backgroundColor: PALETTE.redLight,   borderColor: PALETTE.red,   borderWidth: 1.5, borderRadius: 3 },
        { label: "Diurnal Pattern",  data: data.chart_diurnal_rmse, backgroundColor: PALETTE.blueLight,  borderColor: PALETTE.blue,  borderWidth: 1.5, borderRadius: 3 },
        { label: "Linear Spline",    data: data.chart_linear_rmse,  backgroundColor: PALETTE.amberLight, borderColor: PALETTE.amber, borderWidth: 1.5, borderRadius: 3 },
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { display: true, position: "top", labels: { color: PALETTE.text2, boxWidth: 12, font: { size: 11 } } },
        tooltip: { callbacks: { label: (i) => `  ${i.dataset.label}: RMSE = ${i.raw}` } }
      },
      scales: {
        x: { grid: { display: false }, ticks: tickOpts() },
        y: { grid: gridOpts(), ticks: tickOpts(), beginAtZero: true, title: { display: true, text: "RMSE", color: PALETTE.text2 } }
      }
    }
  });
}

/* ---- Diurnal Dual-Axis Line ---- */
function buildDiurnal(canvas, data) {
  if (!data) return;
  new Chart(canvas, {
    type: "line",
    data: {
      labels: data.hours,
      datasets: [
        {
          label: "AC Power (kW)", data: data.ac_power, yAxisID: "yPower",
          borderColor: PALETTE.amber, backgroundColor: PALETTE.amberLight,
          fill: true, tension: 0.4, pointRadius: 3, borderWidth: 2
        },
        {
          label: "DC Power (kW)", data: data.dc_power, yAxisID: "yPower",
          borderColor: PALETTE.red, borderDash: [4, 3],
          fill: false, tension: 0.4, pointRadius: 2, borderWidth: 1.5
        },
        {
          label: "Irradiance (W/m²)", data: data.irradiation, yAxisID: "yIrrad",
          borderColor: PALETTE.blue, fill: false,
          tension: 0.4, pointRadius: 2, borderWidth: 1.5
        }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { display: true, position: "top", labels: { color: PALETTE.text2, boxWidth: 12, font: { size: 11 } } }
      },
      scales: {
        x: { grid: gridOpts(), ticks: tickOpts({ callback: v => `${v}:00` }) },
        yPower: {
          position: "left", grid: gridOpts(), ticks: tickOpts(),
          title: { display: true, text: "Power (kW)", color: PALETTE.text2 }
        },
        yIrrad: {
          position: "right", grid: { display: false }, ticks: tickOpts(),
          title: { display: true, text: "Irradiance (W/m²)", color: PALETTE.text2 }
        }
      }
    }
  });
}

/* ---- Feature Importance Horizontal Bar ---- */
function buildImportance(canvas, data) {
  if (!data || !data.labels) return;
  new Chart(canvas, {
    type: "bar",
    data: {
      labels: data.labels,
      datasets: [{
        data: data.values,
        backgroundColor: PALETTE.amberLight,
        borderColor: PALETTE.amber,
        borderWidth: 1.5,
        borderRadius: 3
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true, maintainAspectRatio: false,
      plugins: {
        tooltip: { callbacks: { label: (i) => `  Importance: ${i.raw.toFixed(4)}` } }
      },
      scales: {
        x: { grid: gridOpts(), ticks: tickOpts(), beginAtZero: true },
        y: { grid: { display: false }, ticks: tickOpts() }
      }
    }
  });
}

/* ---- Model Comparison Bar ---- */
function buildModelComparison(canvas, data) {
  if (!data) return;
  const colors = data.labels.map(l => l === data.best ? PALETTE.amber : PALETTE.amberLight);
  const borders = data.labels.map(l => l === data.best ? PALETTE.amber : PALETTE.amberMid);
  new Chart(canvas, {
    type: "bar",
    data: {
      labels: data.labels,
      datasets: [{
        data: data.r2,
        backgroundColor: colors,
        borderColor: borders,
        borderWidth: 1.5,
        borderRadius: 4
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        tooltip: { callbacks: { label: (i) => `  R² = ${i.raw}` } }
      },
      scales: {
        x: { grid: { display: false }, ticks: tickOpts() },
        y: { grid: gridOpts(), ticks: tickOpts(), min: 0, max: 1, title: { display: true, text: "R² Score", color: PALETTE.text2 } }
      }
    }
  });
}

/* ---- Predicted vs Actual Scatter ---- */
function buildScatter(canvas, data) {
  if (!data || !data.actual) return;
  const pts = data.actual.map((a, i) => ({ x: a, y: data.pred[i] }));
  const maxVal = Math.max(...data.actual, ...data.pred);
  new Chart(canvas, {
    type: "scatter",
    data: {
      datasets: [
        {
          label: "Predicted vs Actual",
          data: pts,
          backgroundColor: PALETTE.amberLight,
          borderColor: PALETTE.amber,
          pointRadius: 3,
          pointHoverRadius: 5,
        },
        {
          label: "Perfect Fit",
          data: [{ x: 0, y: 0 }, { x: maxVal, y: maxVal }],
          type: "line",
          borderColor: PALETTE.red,
          borderDash: [5, 4],
          borderWidth: 1.5,
          pointRadius: 0,
          fill: false,
        }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { display: true, position: "top", labels: { color: PALETTE.text2, boxWidth: 12, font: { size: 11 } } },
        tooltip: { callbacks: { label: (i) => `  Actual: ${i.raw.x} kW · Pred: ${i.raw.y} kW` } }
      },
      scales: {
        x: { grid: gridOpts(), ticks: tickOpts(), title: { display: true, text: "Actual AC Power (kW)", color: PALETTE.text2 } },
        y: { grid: gridOpts(), ticks: tickOpts(), title: { display: true, text: "Predicted AC Power (kW)", color: PALETTE.text2 } }
      }
    }
  });
}

/* ---- IPI Inverter Bar ---- */
function buildIpiBar(canvas, inverters) {
  if (!inverters || !inverters.length) return;
  const labels = inverters.map(i => i.inverter_id.substring(0, 12) + "…");
  const values = inverters.map(i => i.ipi);
  const colors = values.map(v => v >= 95 ? PALETTE.amberMid : (v >= 85 ? PALETTE.blueLight : PALETTE.redLight));
  const borders = values.map(v => v >= 95 ? PALETTE.amber : (v >= 85 ? PALETTE.blue : PALETTE.red));
  new Chart(canvas, {
    type: "bar",
    data: {
      labels,
      datasets: [{ data: values, backgroundColor: colors, borderColor: borders, borderWidth: 1.5, borderRadius: 3 }]
    },
    options: {
      indexAxis: "y",
      responsive: true, maintainAspectRatio: false,
      plugins: { tooltip: { callbacks: { label: (i) => `  IPI: ${i.raw}%` } } },
      scales: {
        x: { grid: gridOpts(), ticks: tickOpts(), min: 70, max: 110, title: { display: true, text: "IPI %", color: PALETTE.text2 } },
        y: { grid: { display: false }, ticks: tickOpts({ font: { size: 9 } }) }
      }
    }
  });
}

/* ================================================================== DISPATCH */

function dispatch() {
  const D = window.SOLAR_DATA || {};

  document.querySelectorAll("canvas[data-chart]").forEach(canvas => {
    const type = canvas.dataset.chart;
    const key  = canvas.dataset.key;

    switch (type) {

      case "hist":
        if (D.histograms && D.histograms[key])
          buildHist(canvas, D.histograms[key]);
        break;

      case "std":
        if (D.standardized && D.standardized[key])
          buildHist(canvas, D.standardized[key], "rgba(90,152,212,0.22)");
        break;

      case "influence":
        if (D.influence) buildInfluence(canvas, D.influence);
        break;

      case "imputation_benchmark":
        if (D.imputation_lab) buildImputationBenchmark(canvas, D.imputation_lab);
        break;

      case "diurnal":
        if (D.diurnal) buildDiurnal(canvas, D.diurnal);
        break;

      case "importance":
        if (D.importance) buildImportance(canvas, D.importance);
        break;

      case "model_comparison":
        if (D.model_comparison) buildModelComparison(canvas, D.model_comparison);
        break;

      case "scatter":
        if (D.scatter) buildScatter(canvas, D.scatter);
        break;

      case "ipi_bar":
        if (D.inverters) buildIpiBar(canvas, D.inverters);
        break;
    }
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", dispatch);
} else {
  dispatch();
}
