import csv

import pytest

from taskard.database import CSVEncodedList


DB_DIALECT = None


def test_serialization():
    serializer = CSVEncodedList()

    values = ["hello", "world"]
    db_contents = serializer.process_bind_param(values, DB_DIALECT)
    assert db_contents == "hello,world"

    serializer = CSVEncodedList(matrix=True)

    values = [["hello", "world"], ["lorem", "ipsum"]]
    db_contents = serializer.process_bind_param(values, DB_DIALECT)
    assert db_contents == "hello,world\r\nlorem,ipsum"

    values = [["hello", "world"], ["foo", "bar", "baz"], ["lorem", "ipsum"]]
    db_contents = serializer.process_bind_param(values, DB_DIALECT)
    assert db_contents == "hello,world\r\nfoo,bar,baz\r\nlorem,ipsum"


def test_deserialization():
    serializer = CSVEncodedList()

    db_contents = "hello,world"
    values = serializer.process_result_value(db_contents, DB_DIALECT)
    assert values == ["hello", "world"]

    db_contents = "hello,world\r\nlorem,ipsum"

    with pytest.raises(csv.Error):
        serializer.process_result_value(db_contents, DB_DIALECT)

    serializer = CSVEncodedList(matrix=True)

    values = serializer.process_result_value(db_contents, DB_DIALECT)
    assert values == [["hello", "world"], ["lorem", "ipsum"]]

    db_contents = "hello,world\r\nfoo,bar,baz\r\nlorem,ipsum"
    values = serializer.process_result_value(db_contents, DB_DIALECT)
    assert values == [["hello", "world"], ["foo", "bar", "baz"], ["lorem", "ipsum"]]
