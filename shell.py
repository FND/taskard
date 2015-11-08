import atexit

from taskard.web import app, DB
from taskard import commands as cmd
from taskard import models
from taskard.logging import configure_sql_logging

ctx = app.app_context()
ctx.push()
atexit.register(ctx.pop)
configure_sql_logging()
