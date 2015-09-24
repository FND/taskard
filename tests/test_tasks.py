from taskard import commands as cmd

from .fixtures import create_sample_database


def setup_module(module):
    db, module.DB_TEARDOWN = create_sample_database()


def teardown_module(module):
    module.DB_TEARDOWN()


def test_task_retrieval():
    tasks = cmd.retrieve_board_layout("sample")
    assert sorted(tasks.keys()) == ["serious project", "silly project"]
    lane1 = tasks["serious project"]
    lane2 = tasks["silly project"]
    assert sorted(lane1.keys()) == ["done", "in progress", "to do"]
    assert sorted(lane2.keys()) == ["done", "to do"]
    assert _extract("title", lane1["to do"], sort=True) == ["#1", "#3", "#4"]
    assert _extract("title", lane1["in progress"], sort=True) == ["#2", "#5"]
    assert _extract("title", lane1["done"], sort=True) == ["#6"]
    assert _extract("title", lane2["to do"], sort=True) == ["#7"]
    assert _extract("title", lane2["done"], sort=True) == ["#8"]

    tasks = cmd.retrieve_board_layout("sample", lane="silly project")
    assert sorted(tasks.keys()) == ["silly project"]
    lane = tasks["silly project"]
    assert sorted(lane.keys()) == ["done", "to do"]
    assert _extract("title", lane["to do"], sort=True) == ["#7"]
    assert _extract("title", lane["done"], sort=True) == ["#8"]


def _extract(attr, items, sort=False):
    res = [getattr(item, attr) for item in items]
    return sorted(res) if sort else res
