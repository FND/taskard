export PATH := ./venv/bin:$(PATH)

server:
	. venv/bin/activate; python server --dev

shell:
	. venv/bin/activate; python -i -c "import atexit; \
			from taskard.web import app, DB; \
			from taskard import commands as cmd; \
			from taskard import models; \
			from taskard import logging; \
			ctx = app.app_context(); ctx.push(); atexit.register(ctx.pop); \
			logging.activate_sql_logging(app)"

test:
	. venv/bin/activate; py.test -v -x tests

lint:
	pep8 server *.py taskard tests

reset: clean
	rm *.sqlite || true

clean:
	find . -name "*.pyc" | xargs rm || true
	find . -name "__pycache__" | xargs rm -r || true

.PHONY: server shell test lint reset clean
