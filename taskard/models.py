from collections import defaultdict
from uuid import uuid4

from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from sqlalchemy.orm import joinedload, load_only
from sqlalchemy.orm.attributes import flag_modified
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

    @classmethod
    def load(cls, *args):
        """
        retrieves a record, optionally including associated records, while
        limiting retrieval to a set of columns

        if the last argument is a dictionary, it is considered an
        association-columns mapping

        columns to be retrieved are expressed as sequences of column names; if
        that sequence is empty, all columns will be retrieved

            Product.load("name", "price", { Product.vendors: ["address"] })

        this would retrieve products' name and price along with associated
        vendors, for whom only the address is retrieved
        """
        last = args[-1]
        if isinstance(last, dict):
            columns = args[:-1]
            relationships = last
        else:
            columns = args
            relationships = {}

        query = cls.query
        if len(columns):
            query = query.options(load_only(*columns))

        for rel, cols in relationships.items():
            eager = joinedload(rel)
            if cols is not True:
                eager = eager.load_only(*cols)
            query = query.options(eager)

        return query


class Board(db.Model, Record):
    __tablename__ = "boards"

    title = db.Column(db.String, primary_key=True) # TODO: enforce lowercase?
    lanes = db.Column(CSVEncodedList)
    states = db.Column(CSVEncodedList)
    layout = db.Column(CSVEncodedTable)

    tasks = db.relationship("Task", backref="board")
    tasks_query = db.relationship("Task", lazy="dynamic")

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
        flag_modified(self, "layout")

        task.board = self

    def rename_state(self, index, old_name, new_name):
        if new_name in self.states:
            raise ValidationError("state '%s' already exists" % new_name)

        self.states[index] = new_name
        flag_modified(self, "states")

        for lane, states in self.layout.items():
            tasks = states.pop(old_name, None)
            if tasks:
                states[new_name] = tasks
                modified = True
        if modified:
            flag_modified(self, "layout")

    def add_state(self, state):
        dupe = state in self.states

        if not dupe: # re-associate orphans
            lanes = Task.lane.in_(self.lanes)
            orphans = self.tasks_query.filter(lanes).filter_by(state=state).all()

            for orphan in orphans:
                try:
                    tasks = self.layout[orphan.lane]
                except KeyError:
                    self.layout[orphan.lane] = tasks = {}
                try:
                    tasks[orphan.state].append(orphan.id)
                except KeyError:
                    tasks[orphan.state] = [orphan.id]

            if len(orphans):
                flag_modified(self, "layout")

        self.states.append(state)
        flag_modified(self, "states")

        return dupe

    def remove_state(self, state):
        index = self.states.index(state)
        self.states.pop(index)
        flag_modified(self, "states")

        modified = False
        for lane, states in self.layout.items():
            existed = states.pop(state, None)
            if existed:
                modified = True
        if modified:
            flag_modified(self, "layout")

        return index

    def rename_lane(self, index, old_name, new_name):
        if new_name in self.lanes:
            raise ValidationError("lane '%s' already exists" % new_name)

        self.lanes[index] = new_name
        flag_modified(self, "lanes")

        self.layout[new_name] = self.layout.pop(old_name)
        flag_modified(self, "layout")

    def add_lane(self, lane):
        dupe = lane in self.lanes

        if not dupe:
            lane_entries = defaultdict(list)

            # re-associate orphans
            states = Task.state.in_(self.states)
            orphans = self.tasks_query.filter(states).filter_by(lane=lane).all()
            for orphan in orphans:
                lane_entries[orphan.state].append(orphan.id)

            self.layout[lane] = dict(lane_entries)
            flag_modified(self, "layout")

        self.lanes.append(lane)
        flag_modified(self, "lanes")

        return dupe

    def remove_lane(self, lane):
        index = self.lanes.index(lane)
        self.lanes.pop(index)
        flag_modified(self, "lanes")

        self.layout.pop(lane)
        flag_modified(self, "layout")

        return index

    def validate(self):
        if not self.title:
            raise ValidationError("invalid board title")

        if has_duplicates(self.lanes):
            raise ValidationError("lanes must be unique per board")

        if has_duplicates(self.states):
            raise ValidationError("states must be unique per board")

    @property
    def orphaned_tasks(self):
        filters = or_(~Task.lane.in_(self.lanes),
                ~Task.state.in_(self.states))
        return self.tasks_query.filter(filters).all()

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
            tasks = materialized[lane]
            for state in states:
                tasks[state] = (task_index[task_id]
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
