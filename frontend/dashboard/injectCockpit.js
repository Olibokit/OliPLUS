// injectCockpit.js

document.addEventListener("DOMContentLoaded", () => {
  const chartElement = document.getElementById("cockpitChart");
  if (!chartElement) {
    console.warn("📉 Élément #cockpitChart introuvable.");
    return;
  }

  const ctx = chartElement.getContext("2d");

  const cockpitPhases = ["Phase 1 — Structuration", "Phase 2 — Visualisation", "Phase 3 — Annotation"];
  const cockpitProgress = [80, 60, 30];
  const cockpitColors = ["#3b82f6", "#10b981", "#f59e0b"];

  const config = {
    type: "bar",
    data: {
      labels: cockpitPhases,
      datasets: [{
        label: "📊 Progression cockpit",
        data: cockpitProgress,
        backgroundColor: cockpitColors,
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: true,
          labels: {
            color: "#374151",
            font: {
              size: 14,
              family: "Inter"
            }
          }
        },
        title: {
          display: true,
          text: "🧭 État des phases cockpitifiées",
          color: "#111827",
          font: {
            size: 18,
            weight: "bold"
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          ticks: {
            stepSize: 20,
            color: "#4B5563"
          }
        },
        x: {
          ticks: {
            color: "#4B5563"
          }
        }
      }
    }
  };

  new Chart(ctx, config);
});
