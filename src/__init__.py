"""Application Factory principal de WatchLog API."""

import os
from flask import Flask
from src.config import config_by_name
from src.extensions import db, migrate
from src.api import register_api_blueprints


def create_app() -> Flask:
    """
    Construye y regresa la instancia de la app Flask.
    Esta función la usan:
    - flask run en local (app.py)
    - flask db (migraciones)
    - gunicorn en Render (wsgi.py)
    """

    app = Flask(__name__)

    # 1. Cargar configuración según variable FLASK_ENV
    #    development (local), production (Render)
    env_name = os.getenv("FLASK_ENV", "development")
    app.config.from_object(config_by_name[env_name])

    # 2. Inicializar extensiones compartidas
    db.init_app(app)
    migrate.init_app(app, db)

    # 3. Registrar blueprints (/movies, /series, /progress, /health...)
    register_api_blueprints(app)

    return app


__all__ = ["create_app"]

