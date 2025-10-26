from __future__ import annotations
from flask import Blueprint, jsonify, request

from src.api.services import ProgressService

bp = Blueprint("progress", __name__)  # sin url_prefix, las rutas ya están completas

# 👉 instancia reutilizable del servicio
service = ProgressService()


def _require_user_id() -> int:
    """
    Lee el header X-User-Id y lo convierte a int.
    Si falta o es inválido => lanzamos ValueError y respondemos 400.
    """
    raw_id = request.headers.get("X-User-Id")
    if not raw_id:
        raise ValueError("Header X-User-Id es obligatorio.")

    try:
        return int(raw_id)
    except ValueError as exc:
        raise ValueError("X-User-Id debe ser un entero.") from exc


@bp.route("/me/watchlist", methods=["GET"])
def get_my_watchlist():
    """
    Devuelve TODAS las WatchEntry del usuario actual (simulado con el header X-User-Id).
    """
    try:
        user_id = _require_user_id()
    except ValueError as e:
        return jsonify({"detail": str(e)}), 400

    entries = service.list_user_watchlist(user_id)
    # devolvemos cada WatchEntry serializada
    return jsonify([entry.to_dict(include_user=False) for entry in entries]), 200


@bp.route("/watchlist/movies/<int:movie_id>", methods=["POST"])
def add_movie_to_watchlist(movie_id: int):
    """
    Agrega una película a la watchlist del usuario.
    - Si la película no existe -> 404
    - Si ya estaba en la watchlist -> 400
    - Si todo va bien -> 201 con la WatchEntry creada
    """
    try:
        user_id = _require_user_id()
    except ValueError as e:
        return jsonify({"detail": str(e)}), 400

    try:
        entry = service.add_movie(user_id=user_id, movie_id=movie_id)
        return jsonify(entry.to_dict(include_user=False)), 201
    except LookupError as e:
        return jsonify({"detail": str(e)}), 404
    except ValueError as e:
        return jsonify({"detail": str(e)}), 400


@bp.route("/watchlist/series/<int:series_id>", methods=["POST"])
def add_series_to_watchlist(series_id: int):
    """
    Agrega una serie a la watchlist del usuario.
    También inicializa el progreso (temporada 1, episodio 1, etc.).
    """
    try:
        user_id = _require_user_id()
    except ValueError as e:
        return jsonify({"detail": str(e)}), 400

    try:
        entry = service.add_series(user_id=user_id, series_id=series_id)
        return jsonify(entry.to_dict(include_user=False)), 201
    except LookupError as e:
        return jsonify({"detail": str(e)}), 404
    except ValueError as e:
        return jsonify({"detail": str(e)}), 400


@bp.route("/progress/series/<int:series_id>", methods=["PATCH"])
def update_series_progress(series_id: int):
    """
    Actualiza el progreso de una serie ya agregada a la watchlist.
    Body esperado (JSON), por ejemplo:
    {
      "current_season": 2,
      "current_episode": 7,
      "watched_episodes": 20,
      "total_episodes": 12,
      "status": "watching"
    }
    """
    try:
        user_id = _require_user_id()
    except ValueError as e:
        return jsonify({"detail": str(e)}), 400

    data = request.get_json(silent=True) or {}

    try:
        entry = service.update_series_progress(
            user_id=user_id,
            series_id=series_id,
            data=data,
        )
        return jsonify(entry.to_dict(include_user=False)), 200
    except LookupError as e:
        return jsonify({"detail": str(e)}), 404
    except ValueError as e:
        return jsonify({"detail": str(e)}), 400