from flask import Blueprint, request, jsonify
from src.extensions import db
from src.models.movie import Movie

bp = Blueprint("movies", __name__, url_prefix="/movies")

#
# LISTAR TODAS LAS PELÍCULAS
#
@bp.route("/", methods=["GET"])
def list_movies():
    movies = Movie.query.order_by(Movie.created_at.desc()).all()
    return jsonify([m.to_dict() for m in movies]), 200


#
# CREAR UNA PELÍCULA
#
@bp.route("/", methods=["POST"])
def create_movie():
    data = request.get_json() or {}

    title = data.get("title")
    if not title:
        return jsonify({"detail": "Campo 'title' es obligatorio."}), 400

    movie = Movie(
        title=title,
        genre=data.get("genre"),
        release_year=data.get("release_year"),
    )

    db.session.add(movie)
    db.session.commit()
    db.session.refresh(movie)

    return jsonify(movie.to_dict()), 201


#
# OBTENER DETALLE DE UNA PELÍCULA POR ID
#
@bp.route("/<int:movie_id>", methods=["GET"])
def retrieve_movie(movie_id: int):
    movie = Movie.query.get(movie_id)
    if not movie:
        return jsonify({"detail": f"Movie {movie_id} not found"}), 404

    return jsonify(movie.to_dict()), 200
