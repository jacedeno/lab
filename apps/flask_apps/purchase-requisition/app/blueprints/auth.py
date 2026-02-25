import random

import resend
from flask import (
    Blueprint, current_app, flash, redirect, render_template,
    request, session, url_for,
)

from app import db
from app.models import LoginPin

auth_bp = Blueprint('auth', __name__, template_folder='../templates')

ALLOWED_DOMAIN = '@capitolaggregates.com'


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')

    email = request.form.get('email', '').lower().strip()
    if not email or not email.endswith(ALLOWED_DOMAIN):
        flash('Please enter a valid @capitolaggregates.com email address.', 'error')
        return render_template('auth/login.html')

    # Rate limit: 1 PIN per 60 seconds per email
    recent = LoginPin.query.filter(
        LoginPin.email == email,
        LoginPin.created_at > db.func.now() - db.text("INTERVAL '60 seconds'"),
    ).first()
    if recent:
        flash('A PIN was sent recently. Please wait 60 seconds before requesting another.', 'error')
        return render_template('auth/login.html')

    # Generate 6-digit PIN
    pin = f'{random.randint(0, 999999):06d}'

    # Store hashed PIN in DB
    login_pin = LoginPin(email=email)
    login_pin.set_pin(pin)
    db.session.add(login_pin)
    db.session.commit()

    # Send plain-text email via Resend
    api_key = current_app.config.get('RESEND_API_KEY', '')
    if api_key:
        resend.api_key = api_key
        resend.Emails.send({
            'from': 'Capitol Aggregates PR System <noreply@support.cedeno.app>',
            'to': [email],
            'subject': 'Your Login PIN',
            'text': f'Your login PIN is: {pin}\n\nThis PIN expires in 15 minutes.\nDo not share this PIN with anyone.',
        })
    else:
        # Dev mode: log PIN to console
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

    # Find latest valid PIN for this email
    login_pin = LoginPin.query.filter(
        LoginPin.email == email,
        LoginPin.used == False,
        LoginPin.attempts < 5,
    ).order_by(LoginPin.created_at.desc()).first()

    if not login_pin or login_pin.is_expired:
        flash('PIN has expired. Please request a new one.', 'error')
        return render_template('auth/verify.html', email=email)

    if not login_pin.check_pin(pin):
        login_pin.attempts += 1
        db.session.commit()
        remaining = 5 - login_pin.attempts
        if remaining <= 0:
            flash('Too many failed attempts. Please request a new PIN.', 'error')
        else:
            flash(f'Incorrect PIN. {remaining} attempt(s) remaining.', 'error')
        return render_template('auth/verify.html', email=email)

    # Success — mark PIN as used and create session
    login_pin.used = True
    db.session.commit()

    session.permanent = True
    session['user_email'] = email
    session.pop('pending_email', None)

    next_url = request.args.get('next', url_for('main.index'))
    flash('Logged in successfully.', 'success')
    return redirect(next_url)


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))
