from taskard import commands as cmd
from taskard.models import Board

from .fixtures import create_sample_database
from .util import index_tasks


def setup_module(module):
    module.DB, module.DB_TEARDOWN = create_sample_database()


def teardown_module(module):
    module.DB_TEARDOWN()


def test_move():
    load_board = lambda: Board.query.get("sample")

    board = load_board()
    layout = board.layout

    index = index_tasks(board.tasks, "id")
    task_titles = lambda ids: [index[_id].title for _id in ids]

    assert task_titles(layout["serious project"]["to do"]) == ["#1", "#4", "#3"]

    task = next(task for task in board.tasks if task.title == "#4")

    cmd.move_task(DB, task, 0)
    layout = load_board().layout
    assert task_titles(layout["serious project"]["to do"]) == ["#4", "#1", "#3"]

    cmd.move_task(DB, task, 2)
    layout = load_board().layout
    assert task_titles(layout["serious project"]["to do"]) == ["#1", "#3", "#4"]

    cmd.move_task(DB, task, 1)
    layout = load_board().layout
    assert task_titles(layout["serious project"]["to do"]) == ["#1", "#4", "#3"]
