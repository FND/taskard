import csv

from collections import defaultdict
from io import StringIO

from sqlalchemy.types import TypeDecorator, String


class CSVEncodedList(TypeDecorator):
    """
    represents a list of values as CSV string

    `matrix` indicates whether nested lists are to be supported
    """

    impl = String

    def __init__(self, *args, matrix=False, **kwargs):
        super().__init__(*args, **kwargs) # XXX: cargo-culted
        self.matrix = matrix # XXX: misnomer; not actually a matrix, but nested lists

    def process_bind_param(self, values, dialect):
        """
        serialize a list of values (or, with `matrix`, a list of lists of
        values) into a CSV string
        """
        if values is None:
            return None

        output = StringIO()
        writer = csv.writer(output)

        rows = values if self.matrix else [values]
        for row in rows:
            writer.writerow(row)

        return output.getvalue().strip()

    def process_result_value(self, csv_string, dialect):
        """
        deserialize a list of values (or, with `matrix`, a list of lists of
        values) from a CSV string
        """
        if csv_string is None:
            return []

        if self.matrix:
            reader = csv.reader(StringIO(csv_string))
            return list(reader)
        else:
            reader = csv.reader([csv_string])
            return list(reader)[0]


class CSVEncodedTable(CSVEncodedList):

    def __init__(self, rows, columns, *args, **kwargs):
        super().__init__(*args, matrix=True, **kwargs)
        self.rows = rows
        self.columns = columns

    def process_bind_param(self, table, dialect):
        values = []
        for row in self.rows:
            for column in self.columns:
                try:
                    items = table[row][column]
                    values.append([row, column] + items)
                except KeyError:
                    continue

        return super().process_bind_param(values, dialect)

    def process_result_value(self, csv_string, dialect):
        values = super().process_result_value(csv_string, dialect)

        table = defaultdict(dict)
        for items in values:
            row = items.pop(0)
            column = items.pop(0)
            table[row][column] = items

        return dict(table)
