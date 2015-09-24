import csv

import pytest

from taskard.database import CSVEncodedTable, CSVEncodedList


DB_DIALECT = None


def test_simple_serialization():
    serializer = CSVEncodedList()

    values = ["hello", "world"]
    db_contents = serializer.process_bind_param(values, DB_DIALECT)
    assert db_contents == "hello,world"


def test_simple_deserialization():
    serializer = CSVEncodedList()

    db_contents = "hello,world"
    values = serializer.process_result_value(db_contents, DB_DIALECT)
    assert values == ["hello", "world"]

    db_contents = "hello,world\r\nlorem,ipsum"
    with pytest.raises(csv.Error):
        serializer.process_result_value(db_contents, DB_DIALECT)


def test_matrix_serialization():
    serializer = CSVEncodedList(matrix=True)

    values = [["hello", "world"], ["lorem", "ipsum"]]
    db_contents = serializer.process_bind_param(values, DB_DIALECT)
    assert db_contents == "hello,world\r\nlorem,ipsum"

    values = [["hello", "world"], ["foo", "bar", "baz"], ["lorem", "ipsum"]]
    db_contents = serializer.process_bind_param(values, DB_DIALECT)
    assert db_contents == "hello,world\r\nfoo,bar,baz\r\nlorem,ipsum"


def test_matrix_deserialization():
    serializer = CSVEncodedList(matrix=True)

    db_contents = "hello,world\r\nlorem,ipsum"
    values = serializer.process_result_value(db_contents, DB_DIALECT)
    assert values == [["hello", "world"], ["lorem", "ipsum"]]

    db_contents = "hello,world\r\nfoo,bar,baz\r\nlorem,ipsum"
    values = serializer.process_result_value(db_contents, DB_DIALECT)
    assert values == [["hello", "world"], ["foo", "bar", "baz"], ["lorem", "ipsum"]]


def test_table_serialization():
    serializer = CSVEncodedTable()

    values = {
        "serious project": {
            "to do": [1, 3, 5],
            "done": [2, 4]
        },
        "silly project": {
            "to do": [6],
            "in progress": [7],
            "done": [8]
        }
    }
    db_contents = serializer.process_bind_param(values, DB_DIALECT)
    expected = "\r\n".join([
        "serious project,to do,1,3,5",
        "serious project,done,2,4",
        "silly project,to do,6",
        "silly project,in progress,7",
        "silly project,done,8"
    ])
    assert sorted(db_contents.splitlines()) == sorted(expected.splitlines())


def test_table_deserialization():
    serializer = CSVEncodedTable()

    db_contents = "\r\n".join([
        "serious project,to do,1,3,5",
        "serious project,done,2,4",
        "silly project,to do,6",
        "silly project,in progress,7",
        "silly project,done,8"
    ])
    values = serializer.process_result_value(db_contents, DB_DIALECT)
    assert values == {
        "serious project": {
            "to do": ["1", "3", "5"],
            "done": ["2", "4"]
        },
        "silly project": {
            "to do": ["6"],
            "in progress": ["7"],
            "done": ["8"]
        }
    }
