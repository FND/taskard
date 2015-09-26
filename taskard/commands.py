from itertools import groupby

from sqlalchemy.orm import joinedload
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.exc import IntegrityError

from .models import Board, Task


def move_task(db, task, index):
    """
    alters task order within a board sector by repositioning an individual task
    """
    board = task.board
    peers = board.layout[task.lane][task.state]

    _id = task.id
    peers.remove(_id)
    peers.insert(index, _id)

    flag_modified(board, "layout")
    db.session.add(board)
    db.session.commit()


def create_default_board(db, title):
    """
    generates a board prepopulated with basic settings

    raises `ValidationError` for invalid titles, `ConflictError` if a board
    with that title already exists
    """
    board = Board(title, ["sample project"], ["to do", "in progress", "done"])

    task = Task("hello world", "sample project", "to do")
    board.add_task(task)

    db.session.add(board)
    db.session.add(task)
    try:
        db.session.commit()
    except IntegrityError as err:
        raise ConflictError("board '%s' already exists" % board.title) from err

    return board


def retrieve_board_with_tasks(title): # TODO: rename?
    query = Board.query.options(joinedload("tasks"))
    board = query.filter_by(title=title).first()
    if not board:
        raise MissingError("board '%s' does not exist" % title)
    return board


class ConflictError(Exception):
    pass


class MissingError(Exception):
    pass
