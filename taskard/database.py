import csv

from io import StringIO

from sqlalchemy.types import TypeDecorator, VARCHAR


class CSVEncodedList(TypeDecorator):
    """
    represents a list of values as CSV string

    `matrix` indicates whether nested lists are to be supported
    """

    impl = VARCHAR

    def __init__(self, *args, matrix=False, **kwargs):
        super().__init__(*args, **kwargs) # XXX: cargo-culted
        self.matrix = matrix

    def process_bind_param(self, values, dialect):
        if values is None:
            return None

        output = StringIO()
        writer = csv.writer(output)

        rows = values if self.matrix else [values]
        for row in rows:
            writer.writerow(row)

        return output.getvalue().strip()

    def process_result_value(self, value, dialect):
        if value is None:
            return []

        if self.matrix:
            reader = csv.reader(StringIO(value))
            return list(reader)
        else:
            reader = csv.reader([value])
            return list(reader)[0]
