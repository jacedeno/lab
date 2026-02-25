from functools import wraps
from flask import request, g, abort, current_app, session, redirect, url_for

SKIP_AUTH_PATHS = {'/health', '/metrics'}


def init_auth(app):
    @app.before_request
    def identify_user():
        if request.path in SKIP_AUTH_PATHS or request.path.startswith('/static/'):
            return

        # Allow auth routes through without a session
        if request.path.startswith('/auth/'):
            return

        # Session-based auth first, then dev fallback
        email = session.get('user_email', '')
        if not email:
            email = current_app.config.get('DEV_USER_EMAIL', '')

        if not email:
            next_url = request.full_path if request.query_string else request.path
            return redirect(url_for('auth.login', next=next_url))

        g.current_user_email = email.lower().strip()
        g.is_buyer = g.current_user_email in current_app.config['BUYER_EMAILS']

    @app.context_processor
    def inject_user():
        return {
            'current_user_email': getattr(g, 'current_user_email', ''),
            'is_buyer': getattr(g, 'is_buyer', False),
        }


def buyer_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not getattr(g, 'is_buyer', False):
            abort(403, description='Buyer access required')
        return f(*args, **kwargs)
    return decorated
