from datetime import datetime
from src.extensions import db


class WatchEntry(db.Model):
    """
    Representa el progreso de un usuario sobre una película o una serie.

    content_type:
        "movie"  -> content_id apunta a movies.id
        "series" -> content_id apunta a series.id
    """

    __tablename__ = "watch_entries"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    # "movie" o "series"
    content_type = db.Column(db.String(20), nullable=False)

    # id de Movie o de Series, según content_type
    content_id = db.Column(db.Integer, nullable=False)

    status = db.Column(
        db.String(30),
        nullable=False,
        default="watching",  # watching | completed | dropped | planned
    )

    # Progreso específico para series
    current_season = db.Column(db.Integer)
    current_episode = db.Column(db.Integer)

    watched_episodes = db.Column(db.Integer, default=0)
    total_episodes = db.Column(db.Integer, default=0)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Mantener SOLO la relación que sí tiene FK real
    user = db.relationship(
        "User",
        back_populates="watch_entries",
    )

    def percentage_watched(self) -> float:
        """
        Calcula el porcentaje de avance.
        Regla:
        - Si total_episodes es 0 -> 0.0
        - Si status es 'completed' -> 100.0
        - Normal: watched_episodes / total_episodes * 100
        """
        if self.status == "completed":
            return 100.0

        if not self.total_episodes or self.total_episodes <= 0:
            return 0.0

        watched = self.watched_episodes or 0
        total = self.total_episodes or 0

        if watched > total:
            watched = total

        return round((watched / total) * 100.0, 2)

    def to_dict(self, include_user: bool = True) -> dict:
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "content_type": self.content_type,
            "content_id": self.content_id,
            "status": self.status,
            "current_season": self.current_season,
            "current_episode": self.current_episode,
            "watched_episodes": self.watched_episodes,
            "total_episodes": self.total_episodes,
            "percentage_watched": self.percentage_watched(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_user:
            data["user"] = (
                {
                    "id": self.user.id,
                    "name": self.user.name,
                }
                if self.user
                else None
            )

        return data
