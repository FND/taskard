from taskard.models import Board

from .fixtures import create_sample_database
from .util import index_tasks


def setup_module(module):
    db, module.DB_TEARDOWN = create_sample_database()


def teardown_module(module):
    module.DB_TEARDOWN()


def test_layout():
    board = Board.query.get("sample")
    layout = board.layout

    index = index_tasks(board.tasks, "id")
    task_titles = lambda ids: [index[_id].title for _id in ids]

    assert sorted(layout.keys()) == ["serious project", "silly project"]
    lane1 = layout["serious project"]
    lane2 = layout["silly project"]
    assert sorted(lane1.keys()) == ["done", "in progress", "to do"]
    assert sorted(lane2.keys()) == ["done", "to do"]
    assert task_titles(lane1["to do"]) == ["#1", "#4", "#3"]
    assert task_titles(lane1["in progress"]) == ["#5", "#2"]
    assert task_titles(lane1["done"]) == ["#6"]
    assert task_titles(lane2["to do"]) == ["#7"]
    assert task_titles(lane2["done"]) == ["#8"]
