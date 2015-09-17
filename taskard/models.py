from flask.ext.sqlalchemy import SQLAlchemy

from .database import CSVEncodedList


database = db = SQLAlchemy()


class Board(database.Model):

    title = db.Column(db.String, primary_key=True) # TODO: enforce lowercase?
    lanes = db.Column(CSVEncodedList)
    states = db.Column(CSVEncodedList)

    default_lanes = ["my project"]
    default_states = ["to do", "in progress", "done"]

    def __init__(self, title, lanes=None, states=None):
        self.title = title
        self.lanes = self.default_lanes if lanes is None else lanes
        self.states = self.default_states if states is None else states

        self.validate()

    def validate(self):
        if not self.title:
            raise ValidationError("invalid board title")

        if has_duplicates(self.lanes):
            raise ValidationError("lanes must be unique per board")

        if has_duplicates(self.states):
            raise ValidationError("states must be unique per board")


class ValidationError(Exception):
    pass


def has_duplicates(items):
    seen = set()
    for item in items:
        if item in seen:
            return True
        seen.add(item)
    return False
