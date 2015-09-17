import logging
import os

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.orm import mapper

from . import models


logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)


class Database:

    def __init__(self, location):
        self.engine = create_engine("sqlite:///%s" % os.path.abspath(location),
                convert_unicode=True)
        metadata = MetaData(bind=self.engine)

        self.boards = Table("boards", metadata,
                Column("id", Integer, primary_key=True),
                Column("title", String, unique=True))
        mapper(Board, self.boards)

        metadata.create_all()


# NB: model subclasses ensure original classes remain unaltered by `mapper`


class Board(models.Board):
    pass
