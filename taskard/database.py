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
    """
    represents lists of values categorized by row and column as CSV string

        <row>,<column>,<item>,<item>,...
        <row>,<column>,<item>,<item>,...

    this is turned into a dictionary of the form
    `{ <row>: { <column>: [<item>, ...] } }`
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, matrix=True, **kwargs)

    def process_bind_param(self, table, dialect):
        """
        serialize dictionary into a CSV string
        """
        if table is None:
            return None

        values = []
        for row, columns in table.items():
            for column, items in columns.items():
                items = table[row][column]
                values.append([row, column] + items)

        return super().process_bind_param(values, dialect)

    def process_result_value(self, csv_string, dialect):
        """
        deserialize dictionary from a CSV string
        """
        if csv_string is None:
            return {}

        values = super().process_result_value(csv_string, dialect)

        table = defaultdict(dict)
        for items in values:
            row = items.pop(0)
            column = items.pop(0)
            table[row][column] = items

        return dict(table)
