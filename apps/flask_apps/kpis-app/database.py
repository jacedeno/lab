import sqlite3
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime, timedelta


def get_week_start_date(week_num: int) -> Optional[datetime]:
    """Get the Monday start date for a week number in YYWW format."""
    year = 2000 + (week_num // 100)
    week = week_num % 100
    if week < 1 or week > 53:
        return None
    jan4 = datetime(year, 1, 4)
    week1_monday = jan4 - timedelta(days=jan4.weekday())
    return week1_monday + timedelta(weeks=int(week - 1))


def format_week_num(week_num: int) -> int:
    """Convert YYYYWW to YYWW format for display."""
    if week_num > 9999:
        return (week_num // 100 % 100) * 100 + (week_num % 100)
    return week_num


def get_next_week_num(current_week_num: int) -> int:
    """Calculate the next week number in YYWW format."""
    year = current_week_num // 100
    week = current_week_num % 100
    dec_28 = datetime(2000 + year, 12, 28)
    max_week = dec_28.isocalendar()[1]
    if week >= max_week:
        return ((year + 1) * 100) + 1
    return current_week_num + 1


def calculate_averages(data_list: List[Dict]) -> Dict:
    """Calculate averages across a list of week data dicts."""
    if not data_list:
        return {}
    n = len(data_list)
    fields = [
        'Personnel', 'WorkingDays', 'AvailableHours',
        'PlannedHrs_Corrective', 'PlannedHrs_Reliability',
        'ExecutedHrs_Corrective', 'ExecutedHrs_Reliability',
        'PlanningRate', 'PlanAttainment', 'PlanAttainment_Corrective',
        'PlanAttainment_Reliability', 'UnplannedJob_Pct',
        'PMR_Pct', 'PMR_Completion', 'UnplannedHrs_Total'
    ]
    avg = {
        'Week': 'Average',
        'WeekNum': 0,
        'WeekDate': f'{n}-Week Avg',
    }
    for f in fields:
        avg[f] = round(sum(d[f] for d in data_list) / n)
    return avg


class KPIDatabase:
    """Database handler for KPI data persistence"""

    # Column mapping: DB column name -> dict key name
    COLUMN_MAP = {
        'id': 'id',
        'week_name': 'Week',
        'week_num': 'WeekNum',
        'week_date': 'WeekDate',
        'personnel': 'Personnel',
        'working_days': 'WorkingDays',
        'available_hours': 'AvailableHours',
        'planned_hrs_corrective': 'PlannedHrs_Corrective',
        'planned_hrs_reliability': 'PlannedHrs_Reliability',
        'executed_hrs_corrective': 'ExecutedHrs_Corrective',
        'executed_hrs_reliability': 'ExecutedHrs_Reliability',
        'planning_rate': 'PlanningRate',
        'plan_attainment': 'PlanAttainment',
        'plan_attainment_corrective': 'PlanAttainment_Corrective',
        'plan_attainment_reliability': 'PlanAttainment_Reliability',
        'unplanned_job_pct': 'UnplannedJob_Pct',
        'pmr_pct': 'PMR_Pct',
        'pmr_completion': 'PMR_Completion',
        'unplanned_hrs_total': 'UnplannedHrs_Total',
    }

    def __init__(self, db_path: str = "data/kpi_data.db"):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self.conn = None
        self.create_tables()
        self.migrate_week_format()

    def get_connection(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def create_tables(self):
        conn = self.get_connection()
        conn.execute('''
            CREATE TABLE IF NOT EXISTS weeks_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                week_name TEXT UNIQUE NOT NULL,
                week_num INTEGER NOT NULL,
                week_date TEXT NOT NULL,
                personnel INTEGER NOT NULL,
                working_days INTEGER NOT NULL,
                available_hours INTEGER NOT NULL,
                planned_hrs_corrective INTEGER NOT NULL,
                planned_hrs_reliability INTEGER NOT NULL,
                executed_hrs_corrective INTEGER NOT NULL,
                executed_hrs_reliability INTEGER NOT NULL,
                planning_rate INTEGER NOT NULL,
                plan_attainment INTEGER NOT NULL,
                plan_attainment_corrective INTEGER NOT NULL,
                plan_attainment_reliability INTEGER NOT NULL,
                unplanned_job_pct INTEGER NOT NULL,
                pmr_pct INTEGER NOT NULL,
                pmr_completion INTEGER NOT NULL,
                unplanned_hrs_total INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS login_pins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                pin_hash TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                attempts INTEGER DEFAULT 0 NOT NULL,
                used INTEGER DEFAULT 0 NOT NULL
            )
        ''')
        conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_login_pins_email
            ON login_pins (email)
        ''')
        conn.commit()

    def migrate_week_format(self):
        """Migrate existing weeks from 'Week X' format to 'Week YYWW' format."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT week_name, week_num, week_date FROM weeks_data "
            "WHERE week_name LIKE 'Week %'"
        )
        for row in cursor.fetchall():
            week_name = row['week_name']
            parts = week_name.split(' ')
            if len(parts) == 2 and len(parts[1]) == 4 and parts[1].isdigit():
                continue
            try:
                date_obj = self._parse_date(row['week_date'])
                if date_obj:
                    new_name = self._generate_week_name(date_obj)
                    new_num = self._generate_week_sort_key(date_obj)
                    conn.execute(
                        'UPDATE weeks_data SET week_name=?, week_num=? WHERE week_name=?',
                        (new_name, new_num, week_name)
                    )
            except Exception:
                pass
        conn.commit()

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        for fmt in ('%m/%d/%Y', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%y'):
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None

    def _get_iso_week_info(self, date_obj: datetime) -> tuple:
        iso = date_obj.isocalendar()
        return iso[0], iso[1]

    def _generate_week_name(self, date_obj: datetime) -> str:
        year, week = self._get_iso_week_info(date_obj)
        return f"Week {year % 100:02d}{week:02d}"

    def _generate_week_sort_key(self, date_obj: datetime) -> int:
        year, week = self._get_iso_week_info(date_obj)
        return year * 100 + week

    def _row_to_dict(self, row) -> Dict:
        """Convert a sqlite3.Row to a dict with application-level keys."""
        if row is None:
            return None
        d = dict(row)
        result = {}
        for db_col, app_key in self.COLUMN_MAP.items():
            if db_col in d:
                result[app_key] = d[db_col]
        return result

    def add_week(self, week_data: Dict) -> bool:
        conn = self.get_connection()
        try:
            date_obj = self._parse_date(week_data['WeekDate'])
            if date_obj:
                week_name = self._generate_week_name(date_obj)
                week_num = self._generate_week_sort_key(date_obj)
            else:
                week_name = week_data.get('Week', f"Week {week_data['WeekNum']}")
                week_num = week_data['WeekNum']

            conn.execute('''
                INSERT INTO weeks_data (
                    week_name, week_num, week_date, personnel, working_days,
                    available_hours, planned_hrs_corrective, planned_hrs_reliability,
                    executed_hrs_corrective, executed_hrs_reliability,
                    planning_rate, plan_attainment, plan_attainment_corrective,
                    plan_attainment_reliability, unplanned_job_pct, pmr_pct,
                    pmr_completion, unplanned_hrs_total
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                week_name, week_num, week_data['WeekDate'],
                week_data['Personnel'], week_data['WorkingDays'],
                week_data['AvailableHours'],
                week_data['PlannedHrs_Corrective'], week_data['PlannedHrs_Reliability'],
                week_data['ExecutedHrs_Corrective'], week_data['ExecutedHrs_Reliability'],
                week_data['PlanningRate'], week_data['PlanAttainment'],
                week_data['PlanAttainment_Corrective'], week_data['PlanAttainment_Reliability'],
                week_data['UnplannedJob_Pct'], week_data['PMR_Pct'],
                week_data['PMR_Completion'], week_data['UnplannedHrs_Total']
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            print(f"Error adding week: {e}")
            return False

    def get_all_weeks(self) -> List[Dict]:
        conn = self.get_connection()
        rows = conn.execute('''
            SELECT id, week_name, week_num, week_date, personnel, working_days,
                   available_hours, planned_hrs_corrective, planned_hrs_reliability,
                   executed_hrs_corrective, executed_hrs_reliability,
                   planning_rate, plan_attainment, plan_attainment_corrective,
                   plan_attainment_reliability, unplanned_job_pct, pmr_pct,
                   pmr_completion, unplanned_hrs_total
            FROM weeks_data ORDER BY week_num ASC
        ''').fetchall()
        return [self._row_to_dict(r) for r in rows]

    def get_week_by_id(self, week_id: int) -> Optional[Dict]:
        conn = self.get_connection()
        row = conn.execute(
            'SELECT * FROM weeks_data WHERE id = ?', (week_id,)
        ).fetchone()
        return self._row_to_dict(row) if row else None

    def update_week(self, week_id: int, week_data: Dict) -> bool:
        conn = self.get_connection()
        try:
            date_obj = self._parse_date(week_data['WeekDate'])
            if date_obj:
                week_name = self._generate_week_name(date_obj)
                week_num = self._generate_week_sort_key(date_obj)
            else:
                week_name = week_data.get('Week', f"Week {week_data['WeekNum']}")
                week_num = week_data['WeekNum']

            conn.execute('''
                UPDATE weeks_data SET
                    week_name=?, week_num=?, week_date=?, personnel=?,
                    working_days=?, available_hours=?,
                    planned_hrs_corrective=?, planned_hrs_reliability=?,
                    executed_hrs_corrective=?, executed_hrs_reliability=?,
                    planning_rate=?, plan_attainment=?,
                    plan_attainment_corrective=?, plan_attainment_reliability=?,
                    unplanned_job_pct=?, pmr_pct=?, pmr_completion=?,
                    unplanned_hrs_total=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            ''', (
                week_name, week_num, week_data['WeekDate'],
                week_data['Personnel'], week_data['WorkingDays'],
                week_data['AvailableHours'],
                week_data['PlannedHrs_Corrective'], week_data['PlannedHrs_Reliability'],
                week_data['ExecutedHrs_Corrective'], week_data['ExecutedHrs_Reliability'],
                week_data['PlanningRate'], week_data['PlanAttainment'],
                week_data['PlanAttainment_Corrective'], week_data['PlanAttainment_Reliability'],
                week_data['UnplannedJob_Pct'], week_data['PMR_Pct'],
                week_data['PMR_Completion'], week_data['UnplannedHrs_Total'],
                week_id
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating week: {e}")
            return False

    def delete_week(self, week_id: int) -> bool:
        conn = self.get_connection()
        try:
            conn.execute('DELETE FROM weeks_data WHERE id = ?', (week_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting week: {e}")
            return False

    def remove_weeks(self, week_names: List[str]) -> bool:
        conn = self.get_connection()
        try:
            placeholders = ','.join('?' * len(week_names))
            conn.execute(
                f'DELETE FROM weeks_data WHERE week_name IN ({placeholders})',
                week_names
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error removing weeks: {e}")
            return False

    def get_week_count(self) -> int:
        conn = self.get_connection()
        result = conn.execute('SELECT COUNT(*) as count FROM weeks_data').fetchone()
        return result['count'] if result else 0

    def get_latest_weeks(self, n: int = 4) -> List[Dict]:
        conn = self.get_connection()
        rows = conn.execute('''
            SELECT id, week_name, week_num, week_date, personnel, working_days,
                   available_hours, planned_hrs_corrective, planned_hrs_reliability,
                   executed_hrs_corrective, executed_hrs_reliability,
                   planning_rate, plan_attainment, plan_attainment_corrective,
                   plan_attainment_reliability, unplanned_job_pct, pmr_pct,
                   pmr_completion, unplanned_hrs_total
            FROM weeks_data ORDER BY week_num DESC LIMIT ?
        ''', (n,)).fetchall()
        return [self._row_to_dict(r) for r in reversed(rows)]

    def get_weeks_by_nums(self, week_nums: List[int]) -> List[Dict]:
        """Fetch specific weeks by their YYYYWW week_num values."""
        conn = self.get_connection()
        placeholders = ','.join('?' * len(week_nums))
        rows = conn.execute(f'''
            SELECT id, week_name, week_num, week_date, personnel, working_days,
                   available_hours, planned_hrs_corrective, planned_hrs_reliability,
                   executed_hrs_corrective, executed_hrs_reliability,
                   planning_rate, plan_attainment, plan_attainment_corrective,
                   plan_attainment_reliability, unplanned_job_pct, pmr_pct,
                   pmr_completion, unplanned_hrs_total
            FROM weeks_data WHERE week_num IN ({placeholders})
            ORDER BY week_num ASC
        ''', week_nums).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def get_next_week_info(self) -> Dict:
        """Get auto-calculated next week number and date."""
        all_weeks = self.get_all_weeks()
        if all_weeks:
            latest = all_weeks[-1]
            latest_num = format_week_num(latest['WeekNum'])
            next_num = get_next_week_num(latest_num)
        else:
            today = datetime.now()
            iso = today.isocalendar()
            next_num = (iso[0] % 100) * 100 + iso[1]

        monday = get_week_start_date(next_num)
        date_str = monday.strftime('%m/%d/%Y') if monday else datetime.now().strftime('%m/%d/%Y')
        return {'week_num': next_num, 'week_date': date_str}

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
