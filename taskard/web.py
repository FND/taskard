import os

from flask import Flask, render_template, abort, redirect, url_for, request
from sqlalchemy.exc import IntegrityError

from .models import database as DB, Board, ValidationError


app = Flask(__name__, instance_path=os.path.abspath("."),
        instance_relative_config=True)

db_path = os.path.join(app.instance_path, "taskard.sqlite")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_path # TODO: read from instance config
DB.init_app(app)
DB.create_all(app=app)


@app.route("/")
def frontpage():
    return _render("frontpage.html")


@app.route("/boards", methods=["GET", "POST"])
def boards():
    if request.method == "POST":
        title = request.form.get("board-title")
        try:
            board = Board(title)
        except ValidationError as err:
            abort(400, err) # TODO: friendly error

        DB.session.add(board)
        try:
            DB.session.commit()
        except IntegrityError:
            abort(400, "board '%s' already exists" % board.title) # TODO: friendly error

        return redirect(url_for("board", board_id=board.id))

    return _render("boards.html", title="Boards Overview", boards=Board.query.all())


@app.route("/boards/<board_id>")
def board(board_id):
    board = Board.query.filter_by(id=board_id).first()
    if not board:
        abort(404, "board does exist or access is restricted") # TODO: friendly error

    return _render("board.html", title=board.title, board=board)


def _render(template, **params):
    try:
        params["title"] = "%s | Taskard" % params["title"]
    except KeyError:
        params["title"] = "Taskard"

    return render_template(template, **params)
