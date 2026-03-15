# Maintenance KPI Dashboard

A Flask web application for tracking and visualizing weekly maintenance Key Performance Indicators (KPIs) at Capitol Aggregates Inc.

## Features

- **Interactive Dashboard** — 5 KPI metric cards, 6 Chart.js charts, detailed data table, and summary statistics
- **Full CRUD** — Add, edit, and delete weekly KPI data
- **Dynamic Filtering** — Select which weeks to display; averages recalculate based on selection (defaults to last 4 weeks)
- **Color-Coded Alerts** — Visual thresholds for unplanned work (green <15%, orange 15-25%, red >25%)
- **Responsive Design** — Works on desktop and tablet screens
- **Data Migration** — Import tool to transfer data from the previous Streamlit version

## KPIs Tracked

| Metric | Description | Target |
|--------|-------------|--------|
| Planning Rate | Planned hours vs available hours | — |
| Plan Attainment | Executed vs planned hours (Overall, Corrective, Reliability) | 85% |
| Unplanned Jobs | Percentage of reactive/unplanned work | <15% |
| PMR % | Preventive Maintenance Request focus | — |
| PMR Completion | Success rate of preventive maintenance execution | — |

## Tech Stack

- **Backend:** Flask (Python 3.11+)
- **Frontend:** Bootstrap 5, Chart.js, DM Sans + JetBrains Mono fonts
- **Database:** SQLite
- **Production:** Gunicorn, Docker

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
# Clone and navigate to the project
cd ~/repos/lab/apps/flask_apps/kpis-app

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
flask run --debug --port 5000
```

Visit `http://localhost:5000` in your browser.

### Import Data from Streamlit App

If you have existing data in the Streamlit version:

```bash
python tools/import_data.py --source ~/repos/lab/apps/streamlit_apps/kpis-app/data/kpi_data.db
```

## Docker Deployment

```bash
# Build and run
docker compose up -d

# Stop
docker compose down
```

The database is persisted via a Docker volume (`kpi-data`).

## Project Structure

```
kpis-app/
├── app.py                  # Flask application + routes
├── database.py             # SQLite database handler
├── config.py               # App configuration
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container build
├── docker-compose.yml      # Production deployment
├── assets/                 # Company logo + favicon
├── static/
│   ├── css/dashboard.css   # Custom styles
│   └── js/charts.js        # Chart.js configurations
├── templates/              # Jinja2 HTML templates
└── tools/
    └── import_data.py      # Data migration tool
```

## API

### `GET /api/chart-data`

Returns weekly KPI data as JSON for Chart.js rendering.

**Parameters:**
- `weeks` (optional) — Comma-separated week numbers (e.g., `2608,2609,2610,2611`). Defaults to last 4 weeks.

**Response:** JSON object with `weeks` array, `average`, `latest`, and `previous` week data.

## Author

Jose Cedeno — Capitol Aggregates Inc.
