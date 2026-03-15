import os
from datetime import timedelta


class Config:
    """Application configuration"""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "data/kpi_data.db")
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Auth settings
    ALLOWED_EMAIL_DOMAIN = "@capitolaggregates.com"
    RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
    DEV_USER_EMAIL = os.environ.get("DEV_USER_EMAIL", "")
    RESEND_FROM_EMAIL = os.environ.get(
        "RESEND_FROM_EMAIL",
        "Capitol Aggregates KPI Dashboard <noreply@support.cedeno.app>"
    )
