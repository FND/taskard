import os

from flask import Flask, render_template, abort, redirect, url_for, request

from . import commands as cmd
from .config import configure_application
from .models import init_database, Board, Task, ValidationError


app = Flask(__name__, instance_path=os.path.abspath("."),
        instance_relative_config=True)
configure_application(app)

DB = init_database(app)


@app.route("/")
def frontpage():
    boards = Board.load("title")
    return _render("frontpage.html", boards=boards)


@app.route("/boards", methods=["POST"])
def boards():
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


@app.route("/boards/<board_title>", methods=["GET", "POST"])
def board(board_title, edit_mode=False):
    if request.method == "POST":
        form = request.form
        board = Board.load("title", "lanes", "states").get(board_title)

        _update_board_axes(board, form.getlist("lane"), form.getlist("state"))

        edit = True # TODO: edits should not be persisted until saved explicitly
        if "add-lane" in form:
            board.add_lane("")
        elif "add-state" in form:
            board.add_state("")
        elif form.get("rm-lane") is not None:
            board.remove_lane(form["rm-lane"])
        elif form.get("rm-state") is not None:
            board.remove_state(form["rm-state"])
        else:
            edit = False

        DB.session.commit()
        endpoint = "edit_board" if edit else "board"
        return redirect(url_for(endpoint, board_title=board_title))

    board = Board.load({
        Board.tasks: ["id", "title", "board_title"]
    }).get(board_title)
    if not board:
        abort(404, "board '%s' does not exist or access is restricted" % board_title)

    return _render("board.html", title=board.title, board=board)


@app.route("/boards/<board_title>/edit") # XXX: namespace hogging (cf. `task`)
def edit_board(board_title):
    board = Board.load("lanes", "states").get(board_title)
    if not board:
        abort(404, "board '%s' does not exist or access is restricted" % board_title)

    return _render("edit_board.html", title="%s (edit)" % board.title, board=board)


@app.route("/boards/<board_title>/<task_id>")
def task(board_title, task_id):
    task = Task.query.filter_by(id=task_id, board_title=board_title).first()
    if not task:
        abort(404, "task '%s' does not exist or access is restricted" % task_id)
    return "" # TODO


def _render(template, **params):
    try:
        params["title"] = "%s | Taskard" % params["title"]
    except KeyError:
        params["title"] = "Taskard"

    return render_template(template, **params)


def _update_board_axes(board, lanes, states):
    lanes, states = set(lanes), set(states)
    _update_list(set(board.lanes), lanes, board.add_lane, board.remove_lane)
    _update_list(set(board.states), states, board.add_state, board.remove_state)


def _update_list(before, after, add, remove):
    # FIXME: does not support renames (retaining associated tasks)
    for item in before - after:
        remove(item)
    for item in after - before:
        add(item)
