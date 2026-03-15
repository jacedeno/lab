import random
from datetime import datetime, timedelta, timezone

import resend
from flask import (
    Blueprint, current_app, flash, redirect, render_template,
    request, session, url_for, g,
)
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

SKIP_AUTH_PATHS = {'/health'}


def init_auth(app, db):
    """Register auth middleware and context processor."""

    @app.before_request
    def identify_user():
        if request.path in SKIP_AUTH_PATHS:
            return
        if request.path.startswith('/static/') or request.path.startswith('/assets/'):
            return
        if request.path.startswith('/auth/'):
            return

        email = session.get('user_email', '')
        if not email:
            email = current_app.config.get('DEV_USER_EMAIL', '')

        if not email:
            next_url = request.full_path if request.query_string else request.path
            return redirect(url_for('auth.login', next=next_url))

        g.current_user_email = email.lower().strip()

    @app.context_processor
    def inject_user():
        return {
            'current_user_email': getattr(g, 'current_user_email', ''),
        }


def _get_db():
    """Get the KPIDatabase instance from the app."""
    from flask import current_app
    return current_app.config['_db']


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')

    email = request.form.get('email', '').lower().strip()
    domain = current_app.config.get('ALLOWED_EMAIL_DOMAIN', '@capitolaggregates.com')
    if not email or not email.endswith(domain):
        flash(f'Please enter a valid {domain} email address.', 'error')
        return render_template('auth/login.html')

    db = _get_db()
    conn = db.get_connection()

    # Rate limit: 1 PIN per 60 seconds per email
    cutoff = (datetime.now(timezone.utc) - timedelta(seconds=60)).strftime('%Y-%m-%d %H:%M:%S')
    recent = conn.execute(
        'SELECT id FROM login_pins WHERE email = ? AND created_at > ?',
        (email, cutoff)
    ).fetchone()
    if recent:
        flash('A PIN was sent recently. Please wait 60 seconds before requesting another.', 'error')
        return render_template('auth/login.html')

    # Generate 6-digit PIN
    pin = f'{random.randint(0, 999999):06d}'

    # Store hashed PIN
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=15)
    conn.execute(
        'INSERT INTO login_pins (email, pin_hash, created_at, expires_at) VALUES (?, ?, ?, ?)',
        (email, generate_password_hash(pin), now.strftime('%Y-%m-%d %H:%M:%S'),
         expires.strftime('%Y-%m-%d %H:%M:%S'))
    )
    conn.commit()

    # Send email via Resend
    api_key = current_app.config.get('RESEND_API_KEY', '')
    if api_key:
        resend.api_key = api_key
        resend.Emails.send({
            'from': current_app.config.get('RESEND_FROM_EMAIL',
                     'Capitol Aggregates KPI Dashboard <noreply@support.cedeno.app>'),
            'to': [email],
            'subject': 'Your Login PIN — KPI Dashboard',
            'text': f'Your login PIN is: {pin}\n\nThis PIN expires in 15 minutes.\nDo not share this PIN with anyone.',
        })
    else:
        current_app.logger.warning('RESEND_API_KEY not set — PIN for %s: %s', email, pin)

    session['pending_email'] = email
    return redirect(url_for('auth.verify'))


@auth_bp.route('/verify', methods=['GET', 'POST'])
def verify():
    email = session.get('pending_email', '')
    if not email:
        return redirect(url_for('auth.login'))

    if request.method == 'GET':
        return render_template('auth/verify.html', email=email)

    pin = request.form.get('pin', '').strip()
    if not pin or len(pin) != 6 or not pin.isdigit():
        flash('Please enter a valid 6-digit PIN.', 'error')
        return render_template('auth/verify.html', email=email)

    db = _get_db()
    conn = db.get_connection()

    # Find latest valid PIN for this email
    row = conn.execute(
        'SELECT id, pin_hash, created_at, expires_at, attempts, used '
        'FROM login_pins WHERE email = ? AND used = 0 AND attempts < 5 '
        'ORDER BY created_at DESC LIMIT 1',
        (email,)
    ).fetchone()

    if not row:
        flash('PIN has expired. Please request a new one.', 'error')
        return render_template('auth/verify.html', email=email)

    # Check expiry
    expires_at = datetime.strptime(row['expires_at'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) > expires_at:
        flash('PIN has expired. Please request a new one.', 'error')
        return render_template('auth/verify.html', email=email)

    # Verify PIN
    if not check_password_hash(row['pin_hash'], pin):
        new_attempts = row['attempts'] + 1
        conn.execute('UPDATE login_pins SET attempts = ? WHERE id = ?', (new_attempts, row['id']))
        conn.commit()
        remaining = 5 - new_attempts
        if remaining <= 0:
            flash('Too many failed attempts. Please request a new PIN.', 'error')
        else:
            flash(f'Incorrect PIN. {remaining} attempt(s) remaining.', 'error')
        return render_template('auth/verify.html', email=email)

    # Success
    conn.execute('UPDATE login_pins SET used = 1 WHERE id = ?', (row['id'],))
    conn.commit()

    session.permanent = True
    session['user_email'] = email
    session.pop('pending_email', None)

    next_url = request.args.get('next', url_for('dashboard'))
    flash('Logged in successfully.', 'success')
    return redirect(next_url)


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))
