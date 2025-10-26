from typing import List, Optional
from src.extensions import db
from src.models.movie import Movie


class MovieService:
    @staticmethod
    def list_all() -> List[Movie]:
        return Movie.query.order_by(Movie.id.asc()).all()

    @staticmethod
    def get(movie_id: int) -> Optional[Movie]:
        return Movie.query.get(movie_id)

    @staticmethod
    def create(data: dict) -> Movie:
        movie = Movie(
            title=data.get("title"),
            genre=data.get("genre"),
            release_year=data.get("release_year"),
        )
        db.session.add(movie)
        db.session.commit()
        return movie

    @staticmethod
    def update(movie: Movie, data: dict) -> Movie:
        if "title" in data:
            movie.title = data["title"]
        if "genre" in data:
            movie.genre = data["genre"]
        if "release_year" in data:
            movie.release_year = data["release_year"]

        db.session.commit()
        return movie

    @staticmethod
    def delete(movie: Movie) -> None:
        db.session.delete(movie)
        db.session.commit()
