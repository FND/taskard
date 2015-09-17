import csv

from io import StringIO

from sqlalchemy.types import TypeDecorator, VARCHAR


class CSVEncodedList(TypeDecorator):
    """
    represents a list of values as CSV string
    """

    impl = VARCHAR

    def process_bind_param(self, values, dialect):
        if values is None:
            return None

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(values)
        return output.getvalue().strip()

    def process_result_value(self, value, dialect):
        if value is None:
            return []

        reader = csv.reader([value])
        return list(reader)[0]
