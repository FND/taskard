from flask.ext.sqlalchemy import SQLAlchemy


database = db = SQLAlchemy()


class Board(database.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True)

    def __init__(self, title, id=None):
        if not title:
            raise ValidationError("invalid title")

        self.id = id
        self.title = title


class ValidationError(Exception):
    pass
