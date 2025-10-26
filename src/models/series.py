from datetime import datetime
from src.extensions import db


class Series(db.Model):
    __tablename__ = "series"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    total_seasons = db.Column(db.Integer, default=0)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # Relación 1:N con Season
    seasons = db.relationship(
        "Season",
        back_populates="series",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    def to_dict(self, include_seasons: bool = False) -> dict:
        data = {
            "id": self.id,
            "title": self.title,
            "total_seasons": self.total_seasons,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

        if include_seasons:
            data["seasons"] = [
                season.to_dict() for season in self.seasons.all()
            ]

        return data
