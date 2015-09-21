from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declared_attr

from .database import CSVEncodedList


db = SQLAlchemy()


def init_database(app): # TODO: idempotent?
    db.init_app(app)
    db.create_all(app=app)
    return db


class Record:
    """
    mix-in to be used with all models
    """

    # NB: `declared_attr` defers creation, moving the respective column the end

    @declared_attr
    def created_at(cls):
        return db.Column(db.DateTime, server_default=db.func.now())

    @declared_attr
    def updated_at(cls):
        return db.Column(db.DateTime, server_default=db.func.now(),
                onupdate=db.func.now())


class Board(db.Model, Record):
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


class Task(db.Model, Record):
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
        return "<Task '%s' lane='%s' state='%s'>" % (self.title, self.lane, self.state)


class ValidationError(Exception):
    pass


def has_duplicates(items):
    seen = set()
    for item in items:
        if item in seen:
            return True
        seen.add(item)
    return False
