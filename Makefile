export PATH := ./venv/bin:$(PATH)

server:
	. venv/bin/activate; \
			python server --dev

shell:
	mkdir -p tmp
	rm tmp/shell.py || true
	cp "$$PYTHONSTARTUP" tmp/shell.py || true
	{ echo; echo "# ----"; echo; cat shell.py; } >> tmp/shell.py
	. venv/bin/activate; \
			PYTHONSTARTUP=tmp/shell.py TASKARD_CONFIG=development python

test: lint test-unit test-http

test-unit:
	. venv/bin/activate; \
			TASKARD_CONFIG=testing py.test -v -x tests

test-http:
	. venv/bin/activate; \
			python -m taskard.server --mode testing -p 5555 & \
			echo $$! > tests/server.pid; \
			gabbi-run -x -r gabbi_html localhost:5555 < tests/http.yaml; \
			exit_code="$$?"; \
			kill `cat tests/server.pid` && rm tests/server.pid; \
			[ "$$exit_code" -eq 0 ] || false

lint:
	pep8 server *.py taskard tests

reset: clean
	rm *.sqlite || true

clean:
	find . -name "*.pyc" | xargs rm || true
	find . -name "__pycache__" | xargs rm -r || true
	rm -r .cache || true

.PHONY: server shell test test-http test-unit lint reset clean
