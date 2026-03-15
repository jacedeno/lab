// Chart.js global defaults
Chart.defaults.font.family = "'DM Sans', -apple-system, sans-serif";
Chart.defaults.color = '#8d95a0';
Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(255,255,255,0.95)';
Chart.defaults.plugins.tooltip.titleColor = '#1a1a2e';
Chart.defaults.plugins.tooltip.bodyColor = '#5a6474';
Chart.defaults.plugins.tooltip.borderColor = '#e2e6ea';
Chart.defaults.plugins.tooltip.borderWidth = 1;
Chart.defaults.plugins.tooltip.cornerRadius = 8;
Chart.defaults.plugins.tooltip.padding = 10;

const COLORS = {
  primary: '#357b2d',
  secondary: '#4a9d3e',
  accent: '#6bc259',
  lightGreen: '#e8f5e9',
  darkGreen: '#1b5e20',
  orange: '#d4700a',
  warning: '#e67e22',
  danger: '#c0392b',
  coral: '#e08080',
  steelblue: '#4682b4',
};

// Store chart instances for cleanup
let chartInstances = {};

function destroyChart(id) {
  if (chartInstances[id]) {
    chartInstances[id].destroy();
    delete chartInstances[id];
  }
}

async function fetchChartData(weekNums) {
  const params = weekNums.length > 0 ? `?weeks=${weekNums.join(',')}` : '';
  const response = await fetch(`/api/chart-data${params}`);
  return await response.json();
}

function getWeekLabels(weeks) {
  return weeks.map(w => {
    const num = w.WeekNum > 9999
      ? (Math.floor(w.WeekNum / 100) % 100) * 100 + (w.WeekNum % 100)
      : w.WeekNum;
    return String(num);
  });
}

// Chart 1: Plan Attainment Trend
function renderAttainmentChart(data) {
  destroyChart('chartAttainment');
  const ctx = document.getElementById('chartAttainment');
  if (!ctx) return;

  const labels = getWeekLabels(data.weeks);
  chartInstances['chartAttainment'] = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Overall',
          data: data.weeks.map(w => w.PlanAttainment),
          borderColor: COLORS.primary,
          backgroundColor: 'rgba(53, 123, 45, 0.08)',
          borderWidth: 3,
          pointRadius: 5,
          pointBackgroundColor: COLORS.primary,
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          fill: true,
          tension: 0.3,
        },
        {
          label: 'Corrective',
          data: data.weeks.map(w => w.PlanAttainment_Corrective),
          borderColor: COLORS.orange,
          borderWidth: 2,
          borderDash: [6, 4],
          pointRadius: 4,
          pointBackgroundColor: COLORS.orange,
          fill: false,
          tension: 0.3,
        },
        {
          label: 'Reliability',
          data: data.weeks.map(w => w.PlanAttainment_Reliability),
          borderColor: COLORS.secondary,
          borderWidth: 2,
          borderDash: [6, 4],
          pointRadius: 4,
          pointBackgroundColor: COLORS.secondary,
          fill: false,
          tension: 0.3,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: { usePointStyle: true, pointStyle: 'circle', padding: 16, font: { size: 11, weight: '500' } }
        },
        annotation: {
          annotations: {
            targetLine: {
              type: 'line',
              yMin: 85, yMax: 85,
              borderColor: COLORS.danger,
              borderWidth: 1.5,
              borderDash: [6, 4],
              label: {
                display: true,
                content: 'Target 85%',
                position: 'end',
                backgroundColor: 'transparent',
                color: COLORS.danger,
                font: { size: 10, weight: '600', family: "'JetBrains Mono', monospace" },
              }
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: false,
          min: Math.max(0, Math.min(...data.weeks.map(w => Math.min(w.PlanAttainment, w.PlanAttainment_Corrective, w.PlanAttainment_Reliability))) - 10),
          max: 100,
          ticks: { callback: v => v + '%', font: { family: "'JetBrains Mono', monospace", size: 10 } },
          grid: { color: '#eef0f3' },
        },
        x: {
          ticks: { font: { family: "'JetBrains Mono', monospace", size: 10 } },
          grid: { display: false },
        }
      }
    }
  });
}

// Chart 2: Unplanned Work Trend
function renderUnplannedChart(data) {
  destroyChart('chartUnplanned');
  const ctx = document.getElementById('chartUnplanned');
  if (!ctx) return;

  const labels = getWeekLabels(data.weeks);
  const colors = data.weeks.map(w => {
    if (w.UnplannedJob_Pct < 15) return COLORS.primary;
    if (w.UnplannedJob_Pct < 25) return COLORS.warning;
    return COLORS.danger;
  });

  chartInstances['chartUnplanned'] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Unplanned %',
        data: data.weeks.map(w => w.UnplannedJob_Pct),
        backgroundColor: colors.map(c => c + 'dd'),
        borderColor: colors,
        borderWidth: 1,
        borderRadius: 4,
        barPercentage: 0.6,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        annotation: {
          annotations: {
            targetLine: {
              type: 'line',
              yMin: 15, yMax: 15,
              borderColor: COLORS.warning,
              borderWidth: 1.5,
              borderDash: [6, 4],
              label: {
                display: true,
                content: 'Target <15%',
                position: 'end',
                backgroundColor: 'transparent',
                color: COLORS.warning,
                font: { size: 10, weight: '600', family: "'JetBrains Mono', monospace" },
              }
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { callback: v => v + '%', font: { family: "'JetBrains Mono', monospace", size: 10 } },
          grid: { color: '#eef0f3' },
        },
        x: {
          ticks: { font: { family: "'JetBrains Mono', monospace", size: 10 } },
          grid: { display: false },
        }
      }
    }
  });
}

// Chart 3: Resource Utilization
function renderResourceChart(data) {
  destroyChart('chartResource');
  const ctx = document.getElementById('chartResource');
  if (!ctx) return;

  const labels = getWeekLabels(data.weeks);
  chartInstances['chartResource'] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Available Hours',
          data: data.weeks.map(w => w.AvailableHours),
          backgroundColor: COLORS.lightGreen,
          borderColor: '#c8e6c9',
          borderWidth: 1,
          borderRadius: 3,
          barPercentage: 0.5,
          yAxisID: 'y',
        },
        {
          label: 'Executed Hours',
          data: data.weeks.map(w => w.ExecutedHrs_Corrective + w.ExecutedHrs_Reliability),
          backgroundColor: COLORS.primary + 'dd',
          borderColor: COLORS.primary,
          borderWidth: 1,
          borderRadius: 3,
          barPercentage: 0.5,
          yAxisID: 'y',
        },
        {
          label: 'Personnel',
          data: data.weeks.map(w => w.Personnel),
          type: 'line',
          borderColor: COLORS.danger,
          borderWidth: 2,
          pointRadius: 5,
          pointBackgroundColor: COLORS.danger,
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          fill: false,
          yAxisID: 'y1',
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: { usePointStyle: true, pointStyle: 'circle', padding: 16, font: { size: 11, weight: '500' } }
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { font: { family: "'JetBrains Mono', monospace", size: 10 } },
          grid: { color: '#eef0f3' },
          title: { display: true, text: 'Hours', font: { size: 11 } },
        },
        y1: {
          position: 'right',
          beginAtZero: true,
          ticks: { font: { family: "'JetBrains Mono', monospace", size: 10 } },
          grid: { display: false },
          title: { display: true, text: 'Personnel', font: { size: 11 } },
        },
        x: {
          ticks: { font: { family: "'JetBrains Mono', monospace", size: 10 } },
          grid: { display: false },
        }
      }
    }
  });
}

// Chart 4: Planned vs Executed Hours
function renderPlannedExecChart(data) {
  destroyChart('chartPlannedExec');
  const ctx = document.getElementById('chartPlannedExec');
  if (!ctx) return;

  const labels = getWeekLabels(data.weeks);
  chartInstances['chartPlannedExec'] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Planned',
          data: data.weeks.map(w => w.PlannedHrs_Corrective + w.PlannedHrs_Reliability),
          backgroundColor: COLORS.coral + 'bb',
          borderColor: COLORS.coral,
          borderWidth: 1,
          borderRadius: 3,
          barPercentage: 0.6,
        },
        {
          label: 'Executed',
          data: data.weeks.map(w => w.ExecutedHrs_Corrective + w.ExecutedHrs_Reliability),
          backgroundColor: COLORS.secondary + 'dd',
          borderColor: COLORS.secondary,
          borderWidth: 1,
          borderRadius: 3,
          barPercentage: 0.6,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: { usePointStyle: true, pointStyle: 'rectRounded', padding: 16, font: { size: 11, weight: '500' } }
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { font: { family: "'JetBrains Mono', monospace", size: 10 } },
          grid: { color: '#eef0f3' },
          title: { display: true, text: 'Hours', font: { size: 11 } },
        },
        x: {
          ticks: { font: { family: "'JetBrains Mono', monospace", size: 10 } },
          grid: { display: false },
        }
      }
    }
  });
}

// Chart 5: Team Performance
function renderTeamChart(data) {
  destroyChart('chartTeam');
  const ctx = document.getElementById('chartTeam');
  if (!ctx) return;

  const labels = getWeekLabels(data.weeks);
  chartInstances['chartTeam'] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Corrective',
          data: data.weeks.map(w => w.PlanAttainment_Corrective),
          backgroundColor: COLORS.orange + 'cc',
          borderColor: COLORS.orange,
          borderWidth: 1,
          borderRadius: 3,
          barPercentage: 0.6,
        },
        {
          label: 'Reliability',
          data: data.weeks.map(w => w.PlanAttainment_Reliability),
          backgroundColor: COLORS.secondary + 'cc',
          borderColor: COLORS.secondary,
          borderWidth: 1,
          borderRadius: 3,
          barPercentage: 0.6,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: { usePointStyle: true, pointStyle: 'rectRounded', padding: 16, font: { size: 11, weight: '500' } }
        },
        annotation: {
          annotations: {
            targetLine: {
              type: 'line',
              yMin: 85, yMax: 85,
              borderColor: COLORS.danger,
              borderWidth: 1.5,
              borderDash: [6, 4],
              label: {
                display: true,
                content: 'Target 85%',
                position: 'end',
                backgroundColor: 'transparent',
                color: COLORS.danger,
                font: { size: 10, weight: '600', family: "'JetBrains Mono', monospace" },
              }
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: false,
          min: Math.max(0, Math.min(...data.weeks.map(w => Math.min(w.PlanAttainment_Corrective, w.PlanAttainment_Reliability))) - 10),
          max: 100,
          ticks: { callback: v => v + '%', font: { family: "'JetBrains Mono', monospace", size: 10 } },
          grid: { color: '#eef0f3' },
        },
        x: {
          ticks: { font: { family: "'JetBrains Mono', monospace", size: 10 } },
          grid: { display: false },
        }
      }
    }
  });
}

// Chart 6: PMR Performance
function renderPMRChart(data) {
  destroyChart('chartPMR');
  const ctx = document.getElementById('chartPMR');
  if (!ctx) return;

  const labels = getWeekLabels(data.weeks);
  chartInstances['chartPMR'] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'PMR %',
          data: data.weeks.map(w => w.PMR_Pct),
          backgroundColor: COLORS.steelblue + 'bb',
          borderColor: COLORS.steelblue,
          borderWidth: 1,
          borderRadius: 3,
          barPercentage: 0.5,
          yAxisID: 'y',
        },
        {
          label: 'Completion %',
          data: data.weeks.map(w => w.PMR_Completion),
          type: 'line',
          borderColor: COLORS.primary,
          borderWidth: 2.5,
          pointRadius: 5,
          pointBackgroundColor: COLORS.primary,
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          fill: false,
          yAxisID: 'y1',
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: { usePointStyle: true, pointStyle: 'circle', padding: 16, font: { size: 11, weight: '500' } }
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { callback: v => v + '%', font: { family: "'JetBrains Mono', monospace", size: 10 } },
          grid: { color: '#eef0f3' },
          title: { display: true, text: 'PMR %', font: { size: 11 } },
        },
        y1: {
          position: 'right',
          beginAtZero: true,
          max: 100,
          ticks: { callback: v => v + '%', font: { family: "'JetBrains Mono', monospace", size: 10 } },
          grid: { display: false },
          title: { display: true, text: 'Completion %', font: { size: 11 } },
        },
        x: {
          ticks: { font: { family: "'JetBrains Mono', monospace", size: 10 } },
          grid: { display: false },
        }
      }
    }
  });
}

// Main initialization function
async function initDashboardCharts(weekNums) {
  try {
    const data = await fetchChartData(weekNums);
    if (!data.weeks || data.weeks.length === 0) return;

    renderAttainmentChart(data);
    renderUnplannedChart(data);
    renderResourceChart(data);
    renderPlannedExecChart(data);
    renderTeamChart(data);
    renderPMRChart(data);
  } catch (err) {
    console.error('Error loading chart data:', err);
  }
}
