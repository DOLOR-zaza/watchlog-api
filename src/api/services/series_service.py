from typing import List, Optional
from datetime import datetime

from src.extensions import db
from src.models.series import Series
from src.models.seasons import Season


class SeriesService:
    @staticmethod
    def list_all() -> List[Series]:
        """Return todas las series."""
        return Series.query.all()

    @staticmethod
    def create(data: dict) -> Series:
        """
        Crea una serie nueva.
        data esperado:
        {
            "title": "One Piece",
            "total_seasons": 3   # opcional, default 0
        }
        """
        title = data.get("title")
        if not title:
            raise ValueError("Campo 'title' es obligatorio.")

        total_seasons = data.get("total_seasons", 0)

        series = Series(
            title=title,
            total_seasons=total_seasons,
            created_at=datetime.utcnow(),
        )

        db.session.add(series)
        db.session.commit()

        return series

    @staticmethod
    def get_by_id(series_id: int) -> Optional[Series]:
        return Series.query.get(series_id)

    @staticmethod
    def add_season(series_id: int, data: dict) -> Season:
        """
        Agrega una temporada a la serie.
        data esperado:
        {
            "number": 1,
            "episodes_count": 12
        }
        """
        series = SeriesService.get_by_id(series_id)
        if series is None:
            raise LookupError("Series no encontrada.")

        number = data.get("number")
        if number is None:
            raise ValueError("Campo 'number' es obligatorio.")

        episodes_count = data.get("episodes_count", 0)

        season = Season(
            series_id=series.id,
            number=number,
            episodes_count=episodes_count,
        )

        db.session.add(season)

        # actualizar total_seasons si hace falta
        # si agregaste la temporada 4 y total_seasons era 3, lo subimos a 4
        if number > (series.total_seasons or 0):
            series.total_seasons = number

        db.session.commit()

        return season
