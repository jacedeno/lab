import sqlite3
import json
from typing import List, Dict
from pathlib import Path

class KPIDatabase:
    """Database handler for KPI data persistence"""
    
    def __init__(self, db_path: str = "data/kpi_data.db"):
        """Initialize database connection"""
        # Create data directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.db_path = db_path
        self.conn = None
        self.create_tables()
    
    def get_connection(self):
        """Get database connection"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
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
        
        conn.commit()
    
    def add_week(self, week_data: Dict) -> bool:
        """Add a new week to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO weeks_data (
                    week_name, week_num, week_date, personnel, working_days,
                    available_hours, planned_hrs_corrective, planned_hrs_reliability,
                    executed_hrs_corrective, executed_hrs_reliability,
                    planning_rate, plan_attainment, plan_attainment_corrective,
                    plan_attainment_reliability, unplanned_job_pct, pmr_pct,
                    pmr_completion, unplanned_hrs_total
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                week_data['Week'],
                week_data['WeekNum'],
                week_data['WeekDate'],
                week_data['Personnel'],
                week_data['WorkingDays'],
                week_data['AvailableHours'],
                week_data['PlannedHrs_Corrective'],
                week_data['PlannedHrs_Reliability'],
                week_data['ExecutedHrs_Corrective'],
                week_data['ExecutedHrs_Reliability'],
                week_data['PlanningRate'],
                week_data['PlanAttainment'],
                week_data['PlanAttainment_Corrective'],
                week_data['PlanAttainment_Reliability'],
                week_data['UnplannedJob_Pct'],
                week_data['PMR_Pct'],
                week_data['PMR_Completion'],
                week_data['UnplannedHrs_Total']
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Week already exists
            return False
        except Exception as e:
            print(f"Error adding week: {e}")
            return False
    
    def get_all_weeks(self) -> List[Dict]:
        """Get all weeks from the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                week_name as Week,
                week_num as WeekNum,
                week_date as WeekDate,
                personnel as Personnel,
                working_days as WorkingDays,
                available_hours as AvailableHours,
                planned_hrs_corrective as PlannedHrs_Corrective,
                planned_hrs_reliability as PlannedHrs_Reliability,
                executed_hrs_corrective as ExecutedHrs_Corrective,
                executed_hrs_reliability as ExecutedHrs_Reliability,
                planning_rate as PlanningRate,
                plan_attainment as PlanAttainment,
                plan_attainment_corrective as PlanAttainment_Corrective,
                plan_attainment_reliability as PlanAttainment_Reliability,
                unplanned_job_pct as UnplannedJob_Pct,
                pmr_pct as PMR_Pct,
                pmr_completion as PMR_Completion,
                unplanned_hrs_total as UnplannedHrs_Total
            FROM weeks_data
            ORDER BY week_num ASC
        ''')
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def remove_weeks(self, week_names: List[str]) -> bool:
        """Remove weeks from the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            placeholders = ','.join('?' * len(week_names))
            cursor.execute(
                f'DELETE FROM weeks_data WHERE week_name IN ({placeholders})',
                week_names
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error removing weeks: {e}")
            return False
    
    def get_week_count(self) -> int:
        """Get the total number of weeks in the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM weeks_data')
        result = cursor.fetchone()
        return result['count'] if result else 0
    
    def initialize_sample_data(self):
        """Initialize database with sample data if empty"""
        if self.get_week_count() == 0:
            sample_data = [
                {
                    'Week': 'Week 39',
                    'WeekNum': 39,
                    'WeekDate': '9/22/2025',
                    'Personnel': 20,
                    'WorkingDays': 5,
                    'AvailableHours': 728,
                    'PlannedHrs_Corrective': 538,
                    'PlannedHrs_Reliability': 136,
                    'ExecutedHrs_Corrective': 478,
                    'ExecutedHrs_Reliability': 120,
                    'PlanningRate': 93,
                    'PlanAttainment': 89,
                    'PlanAttainment_Corrective': 89,
                    'PlanAttainment_Reliability': 88,
                    'UnplannedJob_Pct': 12,
                    'PMR_Pct': 19,
                    'PMR_Completion': 88,
                    'UnplannedHrs_Total': 89
                },
                {
                    'Week': 'Week 40',
                    'WeekNum': 40,
                    'WeekDate': '9/29/2025',
                    'Personnel': 17,
                    'WorkingDays': 5,
                    'AvailableHours': 576,
                    'PlannedHrs_Corrective': 498,
                    'PlannedHrs_Reliability': 200,
                    'ExecutedHrs_Corrective': 410,
                    'ExecutedHrs_Reliability': 124,
                    'PlanningRate': 121,
                    'PlanAttainment': 77,
                    'PlanAttainment_Corrective': 82,
                    'PlanAttainment_Reliability': 62,
                    'UnplannedJob_Pct': 20,
                    'PMR_Pct': 35,
                    'PMR_Completion': 62,
                    'UnplannedHrs_Total': 124
                },
                {
                    'Week': 'Week 41',
                    'WeekNum': 41,
                    'WeekDate': '10/6/2025',
                    'Personnel': 15,
                    'WorkingDays': 5,
                    'AvailableHours': 496,
                    'PlannedHrs_Corrective': 462,
                    'PlannedHrs_Reliability': 188,
                    'ExecutedHrs_Corrective': 286,
                    'ExecutedHrs_Reliability': 162,
                    'PlanningRate': 131,
                    'PlanAttainment': 69,
                    'PlanAttainment_Corrective': 62,
                    'PlanAttainment_Reliability': 86,
                    'UnplannedJob_Pct': 28,
                    'PMR_Pct': 38,
                    'PMR_Completion': 86,
                    'UnplannedHrs_Total': 102
                }
            ]
            
            for week in sample_data:
                self.add_week(week)
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
