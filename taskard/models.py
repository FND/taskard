from collections import defaultdict
from uuid import uuid4

from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declared_attr

from .database import CSVEncodedTable, CSVEncodedList


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
    layout = db.Column(CSVEncodedTable)

    tasks = db.relationship("Task", backref="board")

    def __init__(self, title, lanes, states):
        self.title = title
        self.lanes = lanes
        self.states = states

        self.validate()

    def add_task(self, task):
        if task.lane not in self.lanes:
            raise ValidationError("invalid lane: '%s'" % task.lane)
        if task.state not in self.states:
            raise ValidationError("invalid state: '%s'" % task.state)

        # TODO: move into separate function/method
        layout = self.layout
        if layout is None: # board not yet persisted
            self.layout = layout = {} # XXX: does not belong here
        lane = task.lane
        state = task.state
        try:
            lane = layout[lane]
        except KeyError:
            layout[lane] = lane = {}
        try:
            lane[state].append(task.id)
        except KeyError:
            lane[state] = [task.id]

        task.board = self

        # TODO: autosave board and task?

    def validate(self):
        if not self.title:
            raise ValidationError("invalid board title")

        if has_duplicates(self.lanes):
            raise ValidationError("lanes must be unique per board")

        if has_duplicates(self.states):
            raise ValidationError("states must be unique per board")

    @property
    def materialized_layout(self): # TODO: rename -- XXX: inefficient
        """
        converts task IDs to actual tasks while traversing layout
        """
        task_index = {}
        for task in self.tasks:
            task_index[task.id] = task

        layout = self.layout
        states = self.states
        materialized = defaultdict(dict)
        for lane in self.lanes:
            lane_entries = layout[lane]
            for state in states:
                materialized[lane][state] = (task_index[task_id]
                        for task_id in lane_entries.get(state, []))
        return dict(materialized)

    def __repr__(self):
        return "<Board '%s'>" % self.title


class Task(db.Model, Record):
    __tablename__ = "tasks"

    id = db.Column(db.CHAR(32), primary_key=True)
    title = db.Column(db.String)
    lane = db.Column(db.String)
    state = db.Column(db.String)
    desc = db.Column(db.Text)

    board_title = db.Column(db.String, db.ForeignKey("boards.title"))

    def __init__(self, title, lane, state, desc=None, id=None):
        # NB: not relying on database to assign ID in order to allow pre-commit
        #     board layout assignment
        self.id = uuid4().hex
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
