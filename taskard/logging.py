import logging


def activate_sql_logging(app):
    app.config['SQLALCHEMY_ECHO'] = True

    sqla_logger = logging.getLogger("sqlalchemy.engine.base.Engine")
    sqla_logger.propagate = False
    sqla_logger.addHandler(SQLLogger())


class SQLLogger(logging.StreamHandler):

    def emit(self, *args, **kwargs):
        self.stream.write("[SQL] ")
        super().emit(*args, **kwargs)
