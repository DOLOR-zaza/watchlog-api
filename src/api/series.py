from flask import Blueprint, request, jsonify
from src.api.services import SeriesService

bp = Blueprint("series", __name__, url_prefix="/series")


@bp.route("/", methods=["GET"])
def list_series():
    """
    Lista todas las series registradas.
    No incluye las seasons dentro (para que la lista sea más liviana).
    """
    all_series = SeriesService.list_all()
    payload = [s.to_dict(include_seasons=False) for s in all_series]
    return jsonify(payload), 200


@bp.route("/", methods=["POST"])
def create_series():
    """
    Crea una nueva serie.
    Body esperado (JSON):
    {
      "title": "Avatar",
      "total_seasons": 1   # opcional
    }
    """
    try:
        data = request.get_json() or {}
        new_series = SeriesService.create(data)

        return jsonify(new_series.to_dict(include_seasons=False)), 201

    except ValueError as e:
        # Ej: falta "title"
        return jsonify({"detail": str(e)}), 400


@bp.route("/<int:series_id>/seasons", methods=["POST"])
def add_season(series_id: int):
    """
    Agrega una temporada nueva a la serie indicada.
    Body esperado (JSON):
    {
      "number": 1,
      "episodes_count": 12
    }

    Devuelve la serie actualizada, con sus seasons.
    """
    try:
        data = request.get_json() or {}
        _season = SeriesService.add_season(series_id, data)

        updated_series = SeriesService.get_by_id(series_id)
        return jsonify(updated_series.to_dict(include_seasons=True)), 201

    except LookupError as e:
        # La serie no existe
        return jsonify({"detail": str(e)}), 404

    except ValueError as e:
        # Ej: falta "number"
        return jsonify({"detail": str(e)}), 400

@bp.route("/<int:series_id>", methods=["GET"])
def get_series(series_id: int):
    from src.models.series import Series
    series = Series.query.get(series_id)
    if not series:
        return jsonify({"detail": f"Series {series_id} not found"}), 404
    # aquí sí queremos seasons incluidas
    return jsonify(series.to_dict(include_seasons=True)), 200
