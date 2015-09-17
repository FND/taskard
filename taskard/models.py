from flask.ext.sqlalchemy import SQLAlchemy

from .database import CSVEncodedList


database = db = SQLAlchemy()


class Board(db.Model):
    __tablename__ = "boards"

    title = db.Column(db.String, primary_key=True) # TODO: enforce lowercase?
    lanes = db.Column(CSVEncodedList)
    states = db.Column(CSVEncodedList)

    tasks = db.relationship("Task", backref="board")

    def __init__(self, title, lanes, states):
        self.title = title
        self.lanes = lanes
        self.states = states

        self.validate()

    def add_task(self, task):
        task.board = self # XXX: hacky?
        if task.lane not in self.lanes:
            raise ValidationError("invalid lane: '%s'" % task.lane)
        if task.state not in self.states:
            raise ValidationError("invalid state: '%s'" % task.state)

    def validate(self):
        if not self.title:
            raise ValidationError("invalid board title")

        if has_duplicates(self.lanes):
            raise ValidationError("lanes must be unique per board")

        if has_duplicates(self.states):
            raise ValidationError("states must be unique per board")

    def __repr__(self):
        return "<Board '%s'>" % self.title


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    lane = db.Column(db.String)
    state = db.Column(db.String)
    desc = db.Column(db.Text)

    board_title = db.Column(db.String, db.ForeignKey("boards.title"))

    def __init__(self, title, lane, state, desc=None, id=None):
        self.id = id
        self.title = title
        self.lane = lane
        self.state = state
        self.desc = desc

    def __repr__(self):
        return "<Task '%s'>" % self.title


class ValidationError(Exception):
    pass


def has_duplicates(items):
    seen = set()
    for item in items:
        if item in seen:
            return True
        seen.add(item)
    return False
