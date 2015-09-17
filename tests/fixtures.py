from flask import Flask

from taskard.models import Board, Task, init_database


def create_sample_database():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:" # TODO: read from instance config

    app_context = app.app_context() # TODO: use `test_request_context`?
    app_context.push()

    db = init_database(app)
    # TODO: reset database?

    board = Board("sample", ["serious project", "silly project", "misc."],
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

    return db, app_context.pop
