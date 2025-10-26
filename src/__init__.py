"""Application Factory principal de WatchLog API."""

import os
from flask import Flask
from src.config import config_by_name  # seguimos usando tu config_by_name
from src.extensions import db, migrate
from src.api import register_api_blueprints

# Importa los modelos para que SQLAlchemy conozca las tablas
# (si no los importamos aquí, db.create_all() no las ve)
from src.models.user import User
from src.models.movie import Movie
from src.models.series import Series
from src.models.seasons import Season
from src.models.watch_entry import WatchEntry


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
    #    "development" (local), "production" (Render)
    env_name = os.getenv("FLASK_ENV", "development")
    app.config.from_object(config_by_name[env_name])

    # 2. Inicializar extensiones compartidas
    db.init_app(app)
    migrate.init_app(app, db)

    # 3. Registrar blueprints (/movies, /series, /progress, /health...)
    register_api_blueprints(app)

    # 4. (Render-friendly) Crear tablas + sembrar usuario demo
    #    Esto corre en cada arranque. En local no molesta,
    #    y en Render nos garantiza que exista app.db y user id=1.
    with app.app_context():
        db.create_all()

        # Semilla mínima: usuario con id=1 para usar X-User-Id: 1
        if db.session.get(User, 1) is None:
            demo_user = User(
                id=1,
                name="Demo",
                email="demo@example.com",
            )
            db.session.add(demo_user)
            db.session.commit()

    return app


__all__ = ["create_app"]
