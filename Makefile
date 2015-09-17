export PATH := ./venv/bin:$(PATH)

server:
	. venv/bin/activate; python server --dev

shell:
	. venv/bin/activate; python

lint:
	pep8 server *.py taskard

reset: clean
	rm *.sqlite || true

clean:
	find . -name "*.pyc" | xargs rm || true
	find . -name "__pycache__" | xargs rm -r || true

.PHONY: server shell lint reset clean
