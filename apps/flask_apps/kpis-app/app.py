from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, jsonify, send_from_directory, abort
)
from config import Config
from database import (
    KPIDatabase, format_week_num, get_week_start_date,
    get_next_week_num, calculate_averages
)
from auth import auth_bp, init_auth

app = Flask(__name__)
app.config.from_object(Config)

db = KPIDatabase(app.config['DATABASE_PATH'])
app.config['_db'] = db  # Make DB accessible to auth module

# Register auth
app.register_blueprint(auth_bp, url_prefix='/auth')
init_auth(app, db)


@app.teardown_appcontext
def close_db(exception):
    pass  # DB connection managed by KPIDatabase singleton


@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory('assets', filename)


@app.route('/')
def dashboard():
    all_weeks = db.get_all_weeks()

    # Determine selected weeks from query param or default to last 4
    weeks_param = request.args.get('weeks', '')
    if weeks_param:
        try:
            selected_nums = [int(w) for w in weeks_param.split(',')]
            # Convert YYWW to YYYYWW for DB lookup
            db_nums = []
            for n in selected_nums:
                if n < 10000:
                    db_nums.append((2000 + n // 100) * 100 + (n % 100))
                else:
                    db_nums.append(n)
            selected_weeks = db.get_weeks_by_nums(db_nums)
        except (ValueError, TypeError):
            selected_weeks = db.get_latest_weeks(4)
    else:
        selected_weeks = db.get_latest_weeks(4)

    # Compute derived data
    latest = selected_weeks[-1] if selected_weeks else None
    previous = selected_weeks[-2] if len(selected_weeks) > 1 else None
    averages = calculate_averages(selected_weeks)

    # Build deltas
    deltas = {}
    if latest and previous:
        for key in ['PlanningRate', 'PlanAttainment', 'UnplannedJob_Pct',
                     'PMR_Pct', 'PMR_Completion']:
            deltas[key] = latest[key] - previous[key]

    # Selected week nums for filter bar (in YYWW format)
    selected_nums_display = [format_week_num(w['WeekNum']) for w in selected_weeks]

    # All available week nums for the "Add weeks" dropdown
    all_week_nums = [
        {'num': format_week_num(w['WeekNum']), 'name': w['Week']}
        for w in all_weeks
    ]

    return render_template('dashboard.html',
        all_weeks=all_weeks,
        selected_weeks=selected_weeks,
        selected_nums=selected_nums_display,
        all_week_nums=all_week_nums,
        latest=latest,
        previous=previous,
        deltas=deltas,
        averages=averages,
        week_count=db.get_week_count(),
        format_week_num=format_week_num,
    )


@app.route('/weeks/add', methods=['GET', 'POST'])
def add_week():
    if request.method == 'POST':
        try:
            week_num = int(request.form['week_num'])
            monday = get_week_start_date(week_num)
            week_date = monday.strftime('%m/%d/%Y') if monday else request.form.get('week_date', '')

            week_data = {
                'Week': f'Week {week_num}',
                'WeekNum': week_num,
                'WeekDate': week_date,
                'Personnel': int(request.form['personnel']),
                'WorkingDays': int(request.form['working_days']),
                'AvailableHours': int(request.form['available_hours']),
                'PlannedHrs_Corrective': int(request.form['planned_hrs_corrective']),
                'PlannedHrs_Reliability': int(request.form['planned_hrs_reliability']),
                'ExecutedHrs_Corrective': int(request.form['executed_hrs_corrective']),
                'ExecutedHrs_Reliability': int(request.form['executed_hrs_reliability']),
                'PlanningRate': int(request.form['planning_rate']),
                'PlanAttainment': int(request.form['plan_attainment']),
                'PlanAttainment_Corrective': int(request.form['plan_attainment_corrective']),
                'PlanAttainment_Reliability': int(request.form['plan_attainment_reliability']),
                'UnplannedJob_Pct': int(request.form['unplanned_job_pct']),
                'PMR_Pct': int(request.form['pmr_pct']),
                'PMR_Completion': int(request.form['pmr_completion']),
                'UnplannedHrs_Total': int(request.form['unplanned_hrs_total']),
            }

            if db.add_week(week_data):
                flash(f'Week {week_num} added successfully.', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash(f'Week {week_num} already exists or could not be added.', 'error')
        except (ValueError, KeyError) as e:
            flash(f'Invalid form data: {e}', 'error')

    next_info = db.get_next_week_info()
    return render_template('add_week.html', next_info=next_info)


@app.route('/weeks/<int:week_id>/edit', methods=['GET', 'POST'])
def edit_week(week_id):
    week = db.get_week_by_id(week_id)
    if not week:
        abort(404)

    if request.method == 'POST':
        try:
            week_num = int(request.form['week_num'])
            monday = get_week_start_date(week_num)
            week_date = monday.strftime('%m/%d/%Y') if monday else request.form.get('week_date', '')

            week_data = {
                'Week': f'Week {week_num}',
                'WeekNum': week_num,
                'WeekDate': week_date,
                'Personnel': int(request.form['personnel']),
                'WorkingDays': int(request.form['working_days']),
                'AvailableHours': int(request.form['available_hours']),
                'PlannedHrs_Corrective': int(request.form['planned_hrs_corrective']),
                'PlannedHrs_Reliability': int(request.form['planned_hrs_reliability']),
                'ExecutedHrs_Corrective': int(request.form['executed_hrs_corrective']),
                'ExecutedHrs_Reliability': int(request.form['executed_hrs_reliability']),
                'PlanningRate': int(request.form['planning_rate']),
                'PlanAttainment': int(request.form['plan_attainment']),
                'PlanAttainment_Corrective': int(request.form['plan_attainment_corrective']),
                'PlanAttainment_Reliability': int(request.form['plan_attainment_reliability']),
                'UnplannedJob_Pct': int(request.form['unplanned_job_pct']),
                'PMR_Pct': int(request.form['pmr_pct']),
                'PMR_Completion': int(request.form['pmr_completion']),
                'UnplannedHrs_Total': int(request.form['unplanned_hrs_total']),
            }

            if db.update_week(week_id, week_data):
                flash(f'Week {week_num} updated successfully.', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Could not update week.', 'error')
        except (ValueError, KeyError) as e:
            flash(f'Invalid form data: {e}', 'error')

    return render_template('edit_week.html', week=week)


@app.route('/weeks/<int:week_id>/delete', methods=['POST'])
def delete_week(week_id):
    week = db.get_week_by_id(week_id)
    if not week:
        abort(404)
    if db.delete_week(week_id):
        flash(f'{week["Week"]} deleted successfully.', 'success')
    else:
        flash('Could not delete week.', 'error')
    return redirect(url_for('manage_weeks'))


@app.route('/weeks')
def manage_weeks():
    all_weeks = db.get_all_weeks()
    return render_template('manage_weeks.html',
        weeks=all_weeks,
        week_count=db.get_week_count(),
        format_week_num=format_week_num,
    )


@app.route('/api/chart-data')
def chart_data():
    weeks_param = request.args.get('weeks', '')
    if weeks_param:
        try:
            selected_nums = [int(w) for w in weeks_param.split(',')]
            db_nums = []
            for n in selected_nums:
                if n < 10000:
                    db_nums.append((2000 + n // 100) * 100 + (n % 100))
                else:
                    db_nums.append(n)
            weeks = db.get_weeks_by_nums(db_nums)
        except (ValueError, TypeError):
            weeks = db.get_latest_weeks(4)
    else:
        weeks = db.get_latest_weeks(4)

    averages = calculate_averages(weeks)
    latest = weeks[-1] if weeks else None
    previous = weeks[-2] if len(weeks) > 1 else None

    return jsonify({
        'weeks': weeks,
        'average': averages,
        'latest': latest,
        'previous': previous,
    })


@app.route('/health')
def health():
    return jsonify({'status': 'ok'}), 200


@app.errorhandler(404)
def not_found(e):
    return render_template('base.html', error_title='404', error_message='Page not found'), 404


if __name__ == '__main__':
    app.run(debug=True, port=5000)
