from src.extensions import db


class Season(db.Model):
    __tablename__ = "seasons"

    id = db.Column(db.Integer, primary_key=True)

    series_id = db.Column(
        db.Integer,
        db.ForeignKey("series.id"),
        nullable=False,
    )

    number = db.Column(db.Integer, nullable=False)  # Temporada 1, 2, 3...
    episodes_count = db.Column(db.Integer, default=0)

    # Relación inversa con Series
    series = db.relationship(
        "Series",
        back_populates="seasons",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "series_id": self.series_id,
            "number": self.number,
            "episodes_count": self.episodes_count,
        }
