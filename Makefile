export PATH := ./venv/bin:$(PATH)

server:
	. venv/bin/activate; python server --dev

lint:
	pep8 server *.py taskard

clean:
	find . -name "*.pyc" | xargs rm || true
	find . -name "__pycache__" | xargs rm -r || true

.PHONY: server lint clean
