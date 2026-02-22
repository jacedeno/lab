import logging
import os
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from prometheus_flask_exporter import PrometheusMetrics

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name=None):
    app = Flask(
        __name__,
        static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static'),
        static_url_path='/static',
    )

    # Configuration
    if config_name == 'production':
        app.config.from_object('app.config.ProductionConfig')
    else:
        app.config.from_object('app.config.DevelopmentConfig')

    # Structured JSON logging to stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        '{"time":"%(asctime)s","level":"%(levelname)s",'
        '"module":"%(module)s","message":"%(message)s"}'
    ))
    app.logger.handlers = [handler]
    app.logger.setLevel(logging.INFO)

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    PrometheusMetrics(app)

    # Auth middleware & context processor
    from app.auth import init_auth
    init_auth(app)

    # Import models so Alembic can detect them
    from app import models  # noqa: F401

    # Blueprints
    from app.blueprints.main import main_bp
    from app.blueprints.requester import requester_bp
    from app.blueprints.buyer import buyer_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(requester_bp, url_prefix='/pr')
    app.register_blueprint(buyer_bp, url_prefix='/buyer')

    return app
