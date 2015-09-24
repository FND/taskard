from flask import Flask

from taskard import commands as cmd
from taskard.models import init_database, Board, Task


def setup_module(module):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    ctx = app.app_context() # TODO: use `test_request_context`?
    ctx.push()
    module.CONTEXT = ctx

    db = init_database(app)
    # TODO: reset database?

    board = Board("dummy", ["serious project", "silly project", "misc."],
            ["to do", "in progress", "done"])
    db.session.add(board)

    tasks = [
        ("#1", "serious project", "to do"),
        ("#4", "serious project", "to do"),
        ("#3", "serious project", "to do"),
        ("#5", "serious project", "in progress"),
        ("#2", "serious project", "in progress"),
        ("#6", "serious project", "done"),
        ("#7", "silly project", "to do"),
        ("#8", "silly project", "done")
    ]
    for (title, lane, state) in tasks:
        task = Task(title, lane, state)
        board.add_task(task)
        db.session.add(task)

    db.session.commit()


def teardown_module(module):
    module.CONTEXT.pop()


def test_task_retrieval():
    tasks = cmd.retrieve_board_layout("dummy")
    assert sorted(tasks.keys()) == ["serious project", "silly project"]
    lane1 = tasks["serious project"]
    lane2 = tasks["silly project"]
    assert sorted(lane1.keys()) == ["done", "in progress", "to do"]
    assert sorted(lane2.keys()) == ["done", "to do"]
    assert _extract("title", lane1["to do"], sort=True) == ["#1", "#3", "#4"]
    assert _extract("title", lane1["in progress"], sort=True) == ["#2", "#5"]
    assert _extract("title", lane1["done"], sort=True) == ["#6"]
    assert _extract("title", lane2["to do"], sort=True) == ["#7"]
    assert _extract("title", lane2["done"], sort=True) == ["#8"]

    tasks = cmd.retrieve_board_layout("dummy", lane="silly project")
    assert sorted(tasks.keys()) == ["silly project"]
    lane = tasks["silly project"]
    assert sorted(lane.keys()) == ["done", "to do"]
    assert _extract("title", lane["to do"], sort=True) == ["#7"]
    assert _extract("title", lane["done"], sort=True) == ["#8"]


def _extract(attr, items, sort=False):
    res = [getattr(item, attr) for item in items]
    return sorted(res) if sort else res
