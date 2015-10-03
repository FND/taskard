import os

from flask import Flask, render_template, abort, redirect, url_for, request

from . import commands as cmd
from .config import configure_application
from .models import init_database, Board, ValidationError


app = Flask(__name__, instance_path=os.path.abspath("."),
        instance_relative_config=True)
configure_application(app)

DB = init_database(app)


@app.route("/")
def frontpage():
    return _render("frontpage.html")


@app.route("/boards", methods=["GET", "POST"])
def boards():
    if request.method == "POST":
        title = request.form.get("board-title")
        try:
            board = cmd.create_default_board(DB, title)
        except ValidationError as err:
            abort(400, err) # TODO: friendly error
        except cmd.ConflictError as err:
            # XXX: revealing existence here is inconsistent with intentionally
            #      unspecific 404 for indivdual boards
            abort(400, err)

        return redirect(url_for("board", board_title=board.title))

    return _render("boards.html", title="Boards Overview", boards=Board.query.all())


@app.route("/boards/<board_title>")
def board(board_title):
    try:
        board = cmd.retrieve_board(board_title, task_attribs=["id", "title"])
    except cmd.MissingError:
        abort(404, "board '%s' does not exist or access is restricted" % board_title)

    return _render("board.html", title=board.title, board=board)


def _render(template, **params):
    try:
        params["title"] = "%s | Taskard" % params["title"]
    except KeyError:
        params["title"] = "Taskard"

    return render_template(template, **params)
