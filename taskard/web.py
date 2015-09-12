import os

from flask import Flask, render_template, abort, redirect, url_for, request

from .models import Board, ValidationError


app = Flask(__name__, instance_relative_config=True)


@app.route("/")
def frontpage():
    return render_template("frontpage.html")


@app.route("/boards", methods=["GET", "POST"])
def boards():
    if request.method == "POST":
        title = request.form.get("board-title")
        try:
            board = Board(title)
        except ValidationError as err:
            abort(400, err) # TODO: friendly error

        store.save(board)

        return redirect(url_for("board", board_id=board.id))

    return render_template("frontpage.html")


@app.route("/boards/<board_id>")
def board(board_id):
    return board_id # TODO
