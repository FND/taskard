from taskard.models import Board, Task

from .fixtures import create_sample_database
from .util import index_tasks


def setup_module(module):
    module.DB, module.DB_TEARDOWN = create_sample_database()


def teardown_module(module):
    module.DB_TEARDOWN()


def test_layout():
    board, layout = _load_board()

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


def test_state_modifications():
    board, layout = _load_board()
    board.add_state("review")
    DB.session.commit()
    board, layout = _load_board()
    assert board.states == ["to do", "in progress", "done", "review"]
    lane1 = layout["serious project"]
    lane2 = layout["silly project"]
    assert sorted(lane1.keys()) == ["done", "in progress", "to do"]
    assert sorted(lane2.keys()) == ["done", "to do"]

    task = Task("#9", "silly project", "review")
    board.add_task(task)
    DB.session.add(task)
    DB.session.commit()
    board, layout = _load_board()
    lane1 = layout["serious project"]
    lane2 = layout["silly project"]
    assert sorted(lane1.keys()) == ["done", "in progress", "to do"]
    assert sorted(lane2.keys()) == ["done", "review", "to do"]
    lane2["review"] == [task.id]

    board.remove_state("review")
    DB.session.commit()
    board, layout = _load_board()
    assert board.states == ["to do", "in progress", "done"]
    lane1 = layout["serious project"]
    lane2 = layout["silly project"]
    assert sorted(lane1.keys()) == ["done", "in progress", "to do"]
    assert sorted(lane2.keys()) == ["done", "to do"]
    assert [t.title for t in board.orphaned_tasks] == ["#9"]

    index = index_tasks(board.tasks, "id")
    task_titles = lambda ids: [index[_id].title for _id in ids]
    board.add_state("review")
    DB.session.commit()
    board, layout = _load_board()
    assert len(board.orphaned_tasks) == 0
    assert task_titles(layout["silly project"]["review"]) == ["#9"]


def test_lane_modifications():
    board, layout = _load_board()
    assert board.lanes == ["serious project", "silly project", "misc."]
    board.add_lane("future project")
    DB.session.commit()
    board, layout = _load_board()
    assert board.lanes == ["serious project", "silly project", "misc.", "future project"]
    assert layout["future project"] == {}

    task = Task("#10", "future project", "to do")
    board.add_task(task)
    DB.session.add(task)
    DB.session.commit()
    board, layout = _load_board()
    assert len(layout["future project"]["to do"]) == 1

    board.remove_lane("future project")
    DB.session.commit()
    board, layout = _load_board()
    assert layout.get("future project") is None
    assert [t.title for t in board.orphaned_tasks] == ["#10"]

    board.remove_lane("silly project")
    DB.session.commit()
    board, layout = _load_board()
    assert layout.get("silly project") is None
    assert [t.title for t in board.orphaned_tasks] == ["#7", "#8", "#9", "#10"]

    index = index_tasks(board.tasks, "id")
    task_titles = lambda ids: [index[_id].title for _id in ids]
    board.add_lane("silly project")
    board.remove_state("review")
    DB.session.commit()
    board, layout = _load_board()
    assert [t.title for t in board.orphaned_tasks] == ["#9", "#10"]
    lane = layout["silly project"]
    assert task_titles(lane["to do"]) == ["#7"]
    assert task_titles(lane["done"]) == ["#8"]


def _load_board():
    DB.session.expire_all() # avoids caching
    board = Board.query.get("sample")
    return board, board.layout
