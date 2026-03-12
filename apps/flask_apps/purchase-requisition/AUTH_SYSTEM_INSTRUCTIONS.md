# Authentication System - Reusable Instructions for CLAUDE.md / AGENTS.md

Copy the relevant sections below into your new app's `CLAUDE.md` or `AGENTS.md`.

---

## Authentication System Specification

This app uses a **passwordless PIN-based authentication** system via email, powered by **Resend** for email delivery. The system is proven and tested in the purchase-requisition app. Replicate it exactly as described below.

### Overview

- Users log in by entering their **company email address**
- A **6-digit numeric PIN** is generated and emailed to them via **Resend**
- The user enters the PIN on a verification page to complete login
- Sessions last **7 days** (`PERMANENT_SESSION_LIFETIME`)
- PINs expire after **15 minutes** and allow a maximum of **5 attempts**
- Rate limit: **1 PIN per 60 seconds** per email address
- PINs are stored **hashed** (werkzeug `generate_password_hash` / `check_password_hash`), never in plain text

### Tech Stack (Auth-Related)

- **Flask** (with Blueprints)
- **Flask-SQLAlchemy** + **Flask-Migrate** (Alembic) with **PostgreSQL**
- **Resend** (`resend>=2.0.0`) for sending PIN emails
- **werkzeug.security** for PIN hashing
- **python-dotenv** for environment variable loading
- PINs are hashed using werkzeug's `generate_password_hash` / `check_password_hash`

### Required Environment Variables

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/<your_db_name>
SECRET_KEY=change-me-in-production
RESEND_API_KEY=<your_resend_api_key>       # Same token used across apps for testing
DEV_USER_EMAIL=dev@capitol.com             # Bypasses login in dev mode (optional, leave empty to force PIN auth)
FLASK_ENV=development
```

> **Note:** The `RESEND_API_KEY` and sender email are shared across apps for testing. Use the same Resend token. The sender address is: `noreply@support.cedeno.app`

### Allowed Email Domain

The login form restricts emails to a specific company domain. Adapt this constant in the auth blueprint:

```python
ALLOWED_DOMAIN = '@capitolaggregates.com'
```

Change this to your app's required domain, or remove the restriction if any email should be allowed.

### Database Model: `LoginPin`

Create this model in `app/models.py`:

```python
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class LoginPin(db.Model):
    __tablename__ = 'login_pins'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), nullable=False, index=True)
    pin_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    expires_at = db.Column(db.DateTime, nullable=False)
    attempts = db.Column(db.Integer, default=0, nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)

    def set_pin(self, pin):
        self.pin_hash = generate_password_hash(pin)
        self.expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

    def check_pin(self, pin):
        return check_password_hash(self.pin_hash, pin)

    @property
    def is_expired(self):
        now = datetime.now(timezone.utc)
        exp = self.expires_at if self.expires_at.tzinfo else self.expires_at.replace(tzinfo=timezone.utc)
        return now > exp

    @property
    def is_valid(self):
        return not self.used and not self.is_expired and self.attempts < 5
```

Generate the migration with: `flask db migrate -m "add login_pins table"` then `flask db upgrade`.

### Auth Blueprint: `app/blueprints/auth.py`

This blueprint handles three routes: `/auth/login`, `/auth/verify`, `/auth/logout`.

```python
import random
import resend
from flask import (
    Blueprint, current_app, flash, redirect, render_template,
    request, session, url_for,
)
from app import db
from app.models import LoginPin

auth_bp = Blueprint('auth', __name__, template_folder='../templates')

ALLOWED_DOMAIN = '@capitolaggregates.com'  # <-- change per app


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')

    email = request.form.get('email', '').lower().strip()
    if not email or not email.endswith(ALLOWED_DOMAIN):
        flash(f'Please enter a valid {ALLOWED_DOMAIN} email address.', 'error')
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

    # Send email via Resend
    api_key = current_app.config.get('RESEND_API_KEY', '')
    if api_key:
        resend.api_key = api_key
        resend.Emails.send({
            'from': 'Your App Name <noreply@support.cedeno.app>',  # <-- change display name per app
            'to': [email],
            'subject': 'Your Login PIN',
            'text': f'Your login PIN is: {pin}\n\nThis PIN expires in 15 minutes.\nDo not share this PIN with anyone.',
        })
    else:
        # Dev mode: log PIN to console so you can still test
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

    # Success
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
```

### Auth Middleware: `app/auth.py`

This runs `before_request` to protect all routes. It also injects `current_user_email` and `is_buyer` into templates via context processor.

```python
from functools import wraps
from flask import request, g, abort, current_app, session, redirect, url_for

SKIP_AUTH_PATHS = {'/health', '/metrics'}


def init_auth(app):
    @app.before_request
    def identify_user():
        if request.path in SKIP_AUTH_PATHS or request.path.startswith('/static/'):
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
        # Role check - adapt 'BUYER_EMAILS' to your app's role list config key
        g.is_buyer = g.current_user_email in current_app.config.get('BUYER_EMAILS', [])

    @app.context_processor
    def inject_user():
        return {
            'current_user_email': getattr(g, 'current_user_email', ''),
            'is_buyer': getattr(g, 'is_buyer', False),
        }


def buyer_required(f):
    """Decorator for routes that require buyer/admin role."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not getattr(g, 'is_buyer', False):
            abort(403, description='Buyer access required')
        return f(*args, **kwargs)
    return decorated
```

### App Factory Wiring (`app/__init__.py`)

In your `create_app()` function, add:

```python
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    # ... config loading ...

    db.init_app(app)
    migrate.init_app(app, db)

    # Auth middleware
    from app.auth import init_auth
    init_auth(app)

    # Import models so Alembic detects them
    from app import models  # noqa: F401

    # Register auth blueprint
    from app.blueprints.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # ... register other blueprints ...
    return app
```

### Config Class (`app/config/__init__.py`)

```python
import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///dev.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
    DEV_USER_EMAIL = os.environ.get('DEV_USER_EMAIL', '')
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
```

### Templates

Create two templates under `app/templates/auth/`:

**`auth/login.html`** - Email input form that POSTs to `url_for('auth.login')`. Single field: `email` (type email). Button text: "Send PIN".

**`auth/verify.html`** - PIN input form that POSTs to `url_for('auth.verify')`. Single field: `pin` (type text, inputmode numeric, pattern `[0-9]{6}`, maxlength 6, autocomplete `one-time-code`). Display the email the PIN was sent to. Include a "Request a new PIN" link back to login.

Both templates should show flash messages for errors/success.

### Required pip Packages (Auth-Related Only)

```
Flask>=3.1.0
Flask-SQLAlchemy>=3.1.1
Flask-Migrate>=4.0.7
psycopg[binary]>=3.1
resend>=2.0.0
python-dotenv>=1.0.1
```

### Role-Based Access (Optional)

The purchase-requisition app uses a `buyers.yaml` file + a `buyers_loader.py` to load privileged emails. If your app needs role-based access:

1. Create `app/config/roles.yaml` (or similar) with a list of privileged user emails
2. Load them in config and store as `app.config['ADMIN_EMAILS']` (or your role name)
3. The `before_request` middleware sets `g.is_admin` based on whether the logged-in email is in that list
4. Use a `@admin_required` decorator (same pattern as `buyer_required`) to protect routes

### Security Features Summary

| Feature | Implementation |
|---|---|
| PIN storage | Hashed with werkzeug (bcrypt-based) |
| PIN expiry | 15 minutes |
| Brute-force protection | Max 5 attempts per PIN |
| Rate limiting | 1 PIN per 60s per email |
| Session duration | 7 days (permanent session) |
| Domain restriction | Configurable `ALLOWED_DOMAIN` constant |
| Dev fallback | `DEV_USER_EMAIL` env var bypasses login (dev only) |
| RESEND_API_KEY not set | PIN logged to console (dev mode) |

### Customization Checklist for New App

- [ ] Change `ALLOWED_DOMAIN` in auth blueprint (or remove domain restriction)
- [ ] Change the `'from'` display name in the Resend email send call
- [ ] Change the email subject/body text if needed
- [ ] Adapt role names (`is_buyer` -> `is_admin`, etc.) to your app's domain
- [ ] Update `SKIP_AUTH_PATHS` if your app has different public endpoints
- [ ] Update the `next_url` default redirect after login (`url_for('main.index')`) to your app's home route
- [ ] Set `RESEND_API_KEY` in `.env` (same token works for testing)
