from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

from .models import Board, Task


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
    return query.filter_by(title=title).first()


class ConflictError(Exception):
    pass
