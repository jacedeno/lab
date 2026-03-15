#!/usr/bin/env python3
"""Import KPI data from the Streamlit app's SQLite database."""

import argparse
import sqlite3
import sys
import os

# Add parent directory to path so we can import database module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import KPIDatabase


DEFAULT_SOURCE = os.path.expanduser(
    "~/repos/lab/apps/streamlit_apps/kpis-app/data/kpi_data.db"
)
DEFAULT_TARGET = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "kpi_data.db"
)


def import_data(source_path: str, target_path: str, dry_run: bool = False):
    """Import weeks from source DB to target DB."""
    if not os.path.exists(source_path):
        print(f"Error: Source database not found at {source_path}")
        sys.exit(1)

    # Read from source
    source_conn = sqlite3.connect(source_path)
    source_conn.row_factory = sqlite3.Row
    rows = source_conn.execute(
        "SELECT * FROM weeks_data ORDER BY week_num ASC"
    ).fetchall()
    source_conn.close()

    total = len(rows)
    print(f"Found {total} weeks in source database.")

    if dry_run:
        for row in rows:
            print(f"  Would import: {row['week_name']} ({row['week_date']})")
        print(f"\nDry run complete. {total} records would be imported.")
        return

    # Write to target
    target_db = KPIDatabase(target_path)
    imported = 0
    skipped = 0

    for row in rows:
        week_data = {
            'Week': row['week_name'],
            'WeekNum': row['week_num'],
            'WeekDate': row['week_date'],
            'Personnel': row['personnel'],
            'WorkingDays': row['working_days'],
            'AvailableHours': row['available_hours'],
            'PlannedHrs_Corrective': row['planned_hrs_corrective'],
            'PlannedHrs_Reliability': row['planned_hrs_reliability'],
            'ExecutedHrs_Corrective': row['executed_hrs_corrective'],
            'ExecutedHrs_Reliability': row['executed_hrs_reliability'],
            'PlanningRate': row['planning_rate'],
            'PlanAttainment': row['plan_attainment'],
            'PlanAttainment_Corrective': row['plan_attainment_corrective'],
            'PlanAttainment_Reliability': row['plan_attainment_reliability'],
            'UnplannedJob_Pct': row['unplanned_job_pct'],
            'PMR_Pct': row['pmr_pct'],
            'PMR_Completion': row['pmr_completion'],
            'UnplannedHrs_Total': row['unplanned_hrs_total'],
        }

        if target_db.add_week(week_data):
            imported += 1
            print(f"  Imported: {row['week_name']} ({row['week_date']})")
        else:
            skipped += 1
            print(f"  Skipped (duplicate): {row['week_name']}")

    target_db.close()
    print(f"\nDone. Imported {imported} of {total} records ({skipped} skipped as duplicates).")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import KPI data from Streamlit app database.')
    parser.add_argument('--source', default=DEFAULT_SOURCE, help='Path to source SQLite database')
    parser.add_argument('--target', default=DEFAULT_TARGET, help='Path to target SQLite database')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be imported without writing')
    args = parser.parse_args()
    import_data(args.source, args.target, args.dry_run)
