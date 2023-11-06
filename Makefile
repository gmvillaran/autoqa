# Run inside src as make -f ../Makefile <command>
format:
	isort .
	black .

lint:
	isort . --check-only
	black . --check
	flake8 . --append-config ../.flake8     

testunit:
	python -m pytest -vv -m "not integration" .

testall:
	python -m pytest -vv .
