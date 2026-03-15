# Maintenance KPI Dashboard (Flask)

## Project Overview

Flask-based web application for tracking weekly maintenance KPIs at Capitol Aggregates Inc. Replaces the previous Streamlit version. Displays performance metrics (Plan Attainment, Planning Rate, Unplanned Work, PMR) with interactive charts and full CRUD for weekly data.

## Tech Stack

- **Backend:** Flask (Python 3.11+)
- **Frontend:** Bootstrap 5 + Chart.js (CDN, no build tooling)
- **Database:** SQLite (`data/kpi_data.db`)
- **Fonts:** DM Sans + JetBrains Mono (Google Fonts CDN)
- **Icons:** Bootstrap Icons (CDN)
- **Production:** Gunicorn + Docker

## Key Files

- `app.py` — Flask app factory, all routes, API endpoint
- `database.py` — KPIDatabase class, SQLite operations, schema management
- `config.py` — Configuration (DB path, app settings)
- `static/css/dashboard.css` — Custom CSS (brand colors, card styles, overrides)
- `static/js/charts.js` — Chart.js configurations for all 6 dashboard charts
- `templates/` — Jinja2 templates (base, dashboard, add/edit week, manage weeks)
- `tools/import_data.py` — Migration tool to import data from Streamlit app DB

## Commands

```bash
# Run development server
flask run --debug --port 5000

# Run with gunicorn (production)
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Import data from Streamlit app
python tools/import_data.py --source ~/repos/lab/apps/streamlit_apps/kpis-app/data/kpi_data.db

# Docker
docker compose up -d
docker compose down
```

## Database

SQLite database at `data/kpi_data.db`. Schema matches the Streamlit version for compatibility. Week format: YYWW (e.g., 2611 = Week 11 of 2026). Week numbers stored as YYYYWW internally for sorting (e.g., 202611).

## Brand Colors

- Primary: `#357b2d` (Capitol Aggregates green)
- Secondary: `#4a9d3e`
- Accent: `#6bc259`
- Warning: `#e67e22`
- Danger: `#c0392b`

## Design Reference

Full dashboard mockup at `.superpowers/brainstorm/77154-1773599704/dashboard-v2.html`. Design spec at `docs/superpowers/specs/2026-03-15-flask-kpi-dashboard-design.md`.

## Important Notes

- All code, comments, and UI must be in English
- No JavaScript build tooling — CDN dependencies only
- Database schema must remain compatible with Streamlit version
- The Streamlit version at `~/repos/lab/apps/streamlit_apps/kpis-app/` is the predecessor
