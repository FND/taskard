import logging

import colorama


def configure_sql_logging():
    sqla_logger = logging.getLogger("sqlalchemy.engine.base.Engine")
    sqla_logger.propagate = False
    sqla_logger.addHandler(SQLLogger(colors=["MAGENTA", "CYAN"]))


class SQLLogger(logging.StreamHandler):

    def __init__(self, stream=None, colors=()):
        super().__init__(stream)
        self.colors = colors
        self.colorizer = Colorizer(self.stream, colors[0])

    def emit(self, record):
        with self.colorizer:
            super().emit(record)

        # cycle colors
        if self.colorizer.active:
            self.colors.append(self.colors.pop(0))
            self.colorizer.color = self.colors[0]


class Colorizer:

    def __init__(self, stream, color):
        self.stream = stream
        self.active = stream.isatty()
        if self.active:
            colorama.init()
            self.color = color

    def __enter__(self):
        if self.active:
            self.stream.write(getattr(colorama.Fore, self.color))

    def __exit__(self, type, value, traceback):
        if self.active:
            self.stream.write(colorama.Fore.RESET)
