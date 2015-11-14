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
    if request.method == "POST": # TODO: conflict detection
        form = request.form
        board = Board.load("title", "lanes", "states", "layout").get(board_title)

        new_lanes = form.getlist("lane")
        old_lanes = list(board.lanes)
        new_states = form.getlist("state")
        old_states = list(board.states)

        edit = True # TODO: edits should not be persisted until saved explicitly
        if "add-lane" in form:
            board.add_lane("")
        elif "add-state" in form:
            board.add_state("")
        elif form.get("rm-lane") is not None:
            index = board.remove_lane(form["rm-lane"])
            new_lanes[index] = old_lanes[index] # avoids renaming
        elif form.get("rm-state") is not None:
            index = board.remove_state(form["rm-state"])
            new_states[index] = old_states[index] # avoids renaming
        else:
            edit = False

        for i, old_name, new_name in _diff(old_lanes, new_lanes):
            board.rename_lane(i, old_name, new_name)
        for i, old_name, new_name in _diff(old_states, new_states):
            board.rename_state(i, old_name, new_name)

        DB.session.commit()
        endpoint = "edit_board" if edit else "board"
        return redirect(url_for(endpoint, board_title=board_title))

    board = Board.load({
        Board.tasks: ["id", "title", "board_title"]
    }).get(board_title)
    if not board:
        abort(404, "board '%s' does not exist or access is restricted" % board_title)

    return _render("board.html", title=board.title, board=board,
            orphaned_tasks=board.orphaned_tasks)


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


def _diff(old_list, new_list):
    for i, new_name in enumerate(new_list):
        old_name = old_list[i]
        if new_name != old_name:
            yield i, old_name, new_name


def _render(template, **params):
    try:
        params["title"] = "%s | Taskard" % params["title"]
    except KeyError:
        params["title"] = "Taskard"

    return render_template(template, **params)
