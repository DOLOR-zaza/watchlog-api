from datetime import datetime
from src.extensions import db


class Movie(db.Model):
    """
    Representa una película individual que un usuario puede agregar a su watchlist.
    """

    __tablename__ = "movies"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(120))
    release_year = db.Column(db.Integer)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # (OJO) quitamos watch_entries porque todavía no tenemos ForeignKey directa
    # watch_entries = db.relationship("WatchEntry", back_populates="movie", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Movie id={self.id} title={self.title!r}>"

    def to_dict(self) -> dict:
        """Serializa la película para respuestas JSON."""
        return {
            "id": self.id,
            "title": self.title,
            "genre": self.genre,
            "release_year": self.release_year,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
