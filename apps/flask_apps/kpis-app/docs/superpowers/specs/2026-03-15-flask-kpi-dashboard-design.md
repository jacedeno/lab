# Flask Maintenance KPI Dashboard — Design Spec

## Overview

A Flask-based web application that replaces the existing Streamlit Maintenance KPI Dashboard. It displays weekly maintenance performance metrics (Plan Attainment, Planning Rate, Unplanned Work, PMR) with full CRUD capabilities, using the same SQLite database schema as the Streamlit version.

**Target directory:** `~/repos/lab/apps/flask_apps/kpis-app/`
**Production URL:** Will replace `kpis.cedeno.app`
**Author:** Jose Cedeno, Capitol Aggregates Inc.

## Tech Stack

- **Backend:** Flask (Python)
- **Frontend:** Bootstrap 5 + Chart.js (CDN, no build tooling)
- **Database:** SQLite (same schema as Streamlit app)
- **Typography:** DM Sans (body) + JetBrains Mono (numeric values)
- **Icons:** Bootstrap Icons

## Project Structure

```
~/repos/lab/apps/flask_apps/kpis-app/
├── app.py                  # Flask application factory + routes
├── database.py             # KPIDatabase class (adapted from Streamlit version)
├── config.py               # Configuration (DB path, app settings)
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container build
├── docker-compose.yml      # Production deployment
├── CLAUDE.md               # Project context for Claude
├── README.md               # Project documentation
├── assets/
│   ├── logo.png            # Company logo (copied from Streamlit app)
│   └── favicon.ico         # Favicon (copied from Streamlit app)
├── static/
│   ├── css/
│   │   └── dashboard.css   # Custom styles (brand colors, cards, overrides)
│   └── js/
│       └── charts.js       # Chart.js chart configurations
├── templates/
│   ├── base.html           # Base layout (navbar, Bootstrap, Chart.js CDN)
│   ├── dashboard.html      # Main dashboard (KPI cards + charts + table)
│   ├── add_week.html       # Add new week form (dedicated page)
│   ├── edit_week.html      # Edit existing week form
│   └── manage_weeks.html   # List/delete weeks
└── tools/
    └── import_data.py      # Migration tool to import from Streamlit DB
```

## Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Dashboard — KPI cards, 6 charts, data table, summary stats |
| `/weeks/add` | GET, POST | Add new week form + submission |
| `/weeks/<id>/edit` | GET, POST | Edit existing week form + submission |
| `/weeks/<id>/delete` | POST | Delete a week (with confirmation) |
| `/weeks` | GET | Manage weeks — list all weeks with edit/delete actions |
| `/api/chart-data` | GET | JSON endpoint for Chart.js (accepts `?weeks=` param) |

## Database

### Schema

Same SQLite schema as the Streamlit app (`weeks_data` table with 20+ columns). The `database.py` module is adapted from the Streamlit version to maintain schema compatibility.

### Data Strategy

The Flask app owns its own database at `data/kpi_data.db`. A migration tool (`tools/import_data.py`) allows importing existing data from the Streamlit app's database. This keeps the apps independent while enabling a smooth transition.

### Key Fields

- `week_name` (TEXT UNIQUE): Week identifier in "Week YYWW" format
- `week_num` (INTEGER): Sortable key in YYYYWW format
- `week_date` (TEXT): Week start date (Monday) in MM/DD/YYYY format
- `personnel`, `working_days`, `available_hours`: Resource metrics
- `planned_hrs_corrective`, `planned_hrs_reliability`: Planning metrics
- `executed_hrs_corrective`, `executed_hrs_reliability`: Execution metrics
- `planning_rate`, `plan_attainment`, `plan_attainment_corrective`, `plan_attainment_reliability`: KPI percentages
- `unplanned_job_pct`, `pmr_pct`, `pmr_completion`, `unplanned_hrs_total`: Additional KPIs

## Navigation

Consistent navbar across all pages matching Capitol Aggregates brand:
- **Left:** Company logo + "Maintenance KPI Dashboard" / "Capitol Aggregates Inc."
- **Right:** "Dashboard" | "Manage Weeks" | [+ Add Week] button

## Dashboard Page (`/`)

### KPI Cards (Top Row)

5 metric cards showing latest week values with delta vs previous week:

1. **Planning Rate** — green accent, up/down indicator
2. **Plan Attainment** — green accent, up/down indicator
3. **Unplanned Jobs** — orange/warning accent, inverse logic (down is good)
4. **PMR %** — green accent, up/down indicator
5. **PMR Completion** — green accent, up/down indicator

Each card includes: label, large monospace value, delta chip (green positive / red negative), mini sparkline in corner.

### Filter Bar

Positioned between KPI cards and charts:
- Week pills (removable) showing selected weeks in monospace font
- "+ Add weeks" button to expand selection
- "Average computed from N selected weeks" meta text
- **Default:** Last 4 weeks from database
- **Behavior:** Changing selection re-fetches chart data and recalculates averages

### Charts (3 Rows × 2 Columns)

All charts rendered with Chart.js, data fetched via `/api/chart-data?weeks=...`.

1. **Plan Attainment Trend** — Line chart with 3 traces (Overall solid, Corrective dashed, Reliability dashed) + 85% target line + area fill under Overall
2. **Unplanned Work Trend** — Bar chart with color coding (green <15%, orange 15-25%, red >25%) + 15% target line
3. **Resource Utilization** — Dual-axis: grouped bars (Available/Executed hours) + line (Personnel count)
4. **Planned vs Executed Hours** — Grouped bar chart (coral planned, green executed)
5. **Team Performance** — Grouped bar chart (Corrective orange, Reliability green) + 85% target line
6. **PMR Performance** — Dual-axis: bars (PMR %) + line (PMR Completion %)

### Data Table

Full-width table with:
- Green header row (uppercase, letter-spaced)
- 11 columns: Week, Date, Personnel, Available Hrs, Planning Rate, Plan Attain., Corrective, Reliability, Unplanned, PMR %, PMR Compl.
- Color-coded status chips for Unplanned % (green/orange/red thresholds)
- Average row at bottom (bold, separated by border) computed from selected weeks only
- Hover highlight on rows

### Summary Statistics (3 Cards)

1. **Selected Period Averages** — Plan Attainment, Planning Rate, Unplanned Work, PMR %, PMR Completion
2. **Team Performance** — Corrective/Reliability Attainment, Avg Personnel, Avg Available Hrs
3. **Latest Week** — Date, Plan Attainment, Unplanned Work, PMR %, Personnel

### Footer

Centered: "Maintenance KPI Dashboard · Capitol Aggregates Inc. · An App by Jose Cedeno"

## Add Week Page (`/weeks/add`)

Dedicated full page with:
- Back button to dashboard
- Auto-calculated next week number (YYWW format) and Monday date
- Form fields organized in a clean grid layout:
  - Week Number (YYWW, auto-populated), Week Date (auto-calculated, read-only)
  - Personnel, Working Days, Available Hours
  - Planned Hrs Corrective, Planned Hrs Reliability
  - Executed Hrs Corrective, Executed Hrs Reliability
  - Planning Rate %, Plan Attainment %, Plan Attainment Corrective %, Plan Attainment Reliability %
  - Unplanned Jobs %, PMR %, PMR Completion %, Unplanned Hours Total
- Save button → redirects to dashboard with success flash message
- Cancel button → returns to dashboard

## Edit Week Page (`/weeks/<id>/edit`)

Same layout as Add Week but pre-populated with existing data. Week number is read-only.

## Manage Weeks Page (`/weeks`)

- Table listing all weeks with columns: Week, Date, Personnel, Plan Attainment, Actions
- Edit button (link to edit page) and Delete button (with confirmation modal) per row
- Total weeks count display

## Visual Design

### Brand Colors

```
--primary:      #357b2d   (main green)
--secondary:    #4a9d3e   (lighter green)
--accent:       #6bc259   (highlight green)
--light-green:  #e8f5e9   (background tint)
--dark-green:   #1b5e20   (deep contrast)
--warning:      #e67e22   (orange for warnings)
--danger:       #c0392b   (red for critical)
```

### Design Principles

- **Refined Industrial Executive** aesthetic — authoritative, data-rich, polished
- Top-border accent on KPI cards (green default, orange for warnings)
- Monospace font (JetBrains Mono) for all numeric values
- Staggered entrance animations on page load
- Sticky navbar with blur backdrop
- Responsive: 5-col → 3-col → 2-col KPI grid, 2-col → 1-col charts
- Shadow hierarchy: sm (cards), md (hover), lg (modals)

### Reference Mockup

Full dashboard mockup available at:
`.superpowers/brainstorm/77154-1773599704/dashboard-v2.html`

## Migration Tool (`tools/import_data.py`)

CLI script that:
1. Accepts source DB path as argument (defaults to Streamlit app location)
2. Reads all weeks from source database
3. Inserts into Flask app's database (skips duplicates)
4. Reports count of imported records

Usage: `python tools/import_data.py --source ~/repos/lab/apps/streamlit_apps/kpis-app/data/kpi_data.db`

## Docker Deployment

- Base image: `python:3.11-slim`
- Port: `5000` (Flask default, configurable)
- Volume: `kpi-data:/app/data` for database persistence
- Assets mounted read-only
- Health check: `curl --fail http://localhost:5000/`
- Gunicorn as WSGI server for production

## API Endpoint

### `GET /api/chart-data`

**Parameters:**
- `weeks` (optional): Comma-separated week numbers (e.g., `2608,2609,2610,2611`). Defaults to last 4 weeks.

**Response:**
```json
{
  "weeks": [
    {
      "Week": "Week 2608",
      "WeekNum": 202608,
      "WeekDate": "02/16/2026",
      "Personnel": 15,
      "AvailableHours": 496,
      "PlannedHrs_Corrective": 462,
      "PlannedHrs_Reliability": 188,
      "ExecutedHrs_Corrective": 286,
      "ExecutedHrs_Reliability": 162,
      "PlanningRate": 97,
      "PlanAttainment": 65,
      "PlanAttainment_Corrective": 60,
      "PlanAttainment_Reliability": 78,
      "UnplannedJob_Pct": 28,
      "PMR_Pct": 30,
      "PMR_Completion": 75,
      "UnplannedHrs_Total": 102
    }
  ],
  "average": { ... },
  "latest": { ... },
  "previous": { ... }
}
```

## Constraints

- All code, comments, and UI text must be in English
- No JavaScript build tooling — CDN only (Bootstrap, Chart.js, Google Fonts)
- Single `app.py` file — no blueprints (app is simple enough)
- Must maintain schema compatibility with Streamlit app's database
