from flask.ext.sqlalchemy import SQLAlchemy

from .database import CSVEncodedList


database = db = SQLAlchemy()


class Board(database.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True)
    states = db.Column(CSVEncodedList)

    default_states = ["to do", "in progress", "done"]

    def __init__(self, title, states=None, id=None):
        if not title:
            raise ValidationError("invalid title")

        self.id = id
        self.title = title
        self.states = self.default_states if states is None else states
        if has_duplicates(self.states):
            raise ValidationError("board states must be unique")


class ValidationError(Exception):
    pass


def has_duplicates(items):
    seen = set()
    for item in items:
        if item in seen:
            return True
        seen.add(item)
    return False
