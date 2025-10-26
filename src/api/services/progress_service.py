# src/api/services/progress_service.py

from datetime import datetime
from src.extensions import db
from src.models.user import User
from src.models.movie import Movie
from src.models.series import Series
from src.models.watch_entry import WatchEntry


class ProgressService:
    """
    Lógica de:
    - watchlist del usuario
    - agregar contenido
    - actualizar progreso
    """

    # ---------- helpers internos ----------

    @staticmethod
    def _get_user(user_id: int) -> User:
        user = db.session.get(User, user_id)
        if not user:
            raise LookupError(f"Usuario {user_id} no existe")
        return user

    @staticmethod
    def _get_movie(movie_id: int) -> Movie:
        movie = db.session.get(Movie, movie_id)
        if not movie:
            raise LookupError(f"Pelicula {movie_id} no existe")
        return movie

    @staticmethod
    def _get_series(series_id: int) -> Series:
        series = db.session.get(Series, series_id)
        if not series:
            raise LookupError(f"Serie {series_id} no existe")
        return series

    @staticmethod
    def _find_watch_entry(user_id: int, content_type: str, content_id: int) -> WatchEntry | None:
        return (
            WatchEntry.query.filter_by(
                user_id=user_id,
                content_type=content_type,
                content_id=content_id,
            )
            .order_by(WatchEntry.id.desc())
            .first()
        )

    # ---------- API pública que usa el blueprint ----------

    @staticmethod
    def list_user_watchlist(user_id: int) -> list[WatchEntry]:
        """
        Devuelve todas las WatchEntry de un usuario.
        """
        ProgressService._get_user(user_id)  # valida que exista

        return (
            WatchEntry.query.filter_by(user_id=user_id)
            .order_by(WatchEntry.created_at.desc())
            .all()
        )

    @staticmethod
    def add_movie(user_id: int, movie_id: int) -> WatchEntry:
        """
        Agrega una pelicula a la watchlist del usuario.
        - si ya existe esa entrada -> ValueError
        """
        user = ProgressService._get_user(user_id)
        movie = ProgressService._get_movie(movie_id)

        already = ProgressService._find_watch_entry(
            user_id=user.id,
            content_type="movie",
            content_id=movie.id,
        )
        if already:
            raise ValueError("La película ya está en tu watchlist")

        entry = WatchEntry(
            user_id=user.id,
            content_type="movie",
            content_id=movie.id,
            status="watching",
            watched_episodes=1,     # para película tratamos como '1 de 1'
            total_episodes=1,
            current_season=None,
            current_episode=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        db.session.add(entry)
        db.session.commit()
        db.session.refresh(entry)
        return entry

    @staticmethod
    def add_series(user_id: int, series_id: int) -> WatchEntry:
        """
        Agrega una serie a la watchlist con progreso inicial.
        - si ya existe esa entrada -> ValueError
        - total_episodes se calcula sumando todos los episodios declarados
          en las temporadas (seasons) de esa serie.
        """
        user = ProgressService._get_user(user_id)
        series = ProgressService._get_series(series_id)

        already = ProgressService._find_watch_entry(
            user_id=user.id,
            content_type="series",
            content_id=series.id,
        )
        if already:
            raise ValueError("La serie ya está en tu watchlist")

        # NUEVO: calcular total de episodios declarados en las seasons
        total_eps = 0
        # series.seasons es una relación lazy="dynamic", así que necesitamos .all()
        for season in series.seasons.all():
            if season.episodes_count:
                total_eps += season.episodes_count

        entry = WatchEntry(
            user_id=user.id,
            content_type="series",
            content_id=series.id,
            status="watching",
            current_season=1,
            current_episode=1,
            watched_episodes=0,
            total_episodes=total_eps,   # <-- antes era 0 fijo
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        db.session.add(entry)
        db.session.commit()
        db.session.refresh(entry)
        return entry

    @staticmethod
    def update_series_progress(user_id: int, series_id: int, data: dict) -> WatchEntry:
        """
        Modifica el progreso de una serie existente en la watchlist.
        """
        entry = ProgressService._find_watch_entry(
            user_id=user_id,
            content_type="series",
            content_id=series_id,
        )
        if not entry:
            raise LookupError("Todavia no agregaste esa serie a tu watchlist")

        allowed_fields = [
            "current_season",
            "current_episode",
            "watched_episodes",
            "total_episodes",
            "status",
        ]

        for field in allowed_fields:
            if field in data:
                setattr(entry, field, data[field])

        entry.updated_at = datetime.utcnow()
        db.session.commit()
        db.session.refresh(entry)
        return entry
