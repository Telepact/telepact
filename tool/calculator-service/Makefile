PYPROJECT = pyproject.toml
MSGPACT_DEP_VERSION_FILE = ../../lib/py/VERSION.txt
SCHEMA_FILE = ../../qa/test/schema/calculator/calculator.msgpact.json
COPIED_SCHEMA_FILE = calculator_service/calculator.msgpact.json

.PHONY: all dep

all: dep $(PYPROJECT) $(COPIED_SCHEMA_FILE)

$(COPIED_SCHEMA_FILE): $(SCHEMA_FILE)
	cp $(SCHEMA_FILE) $(COPIED_SCHEMA_FILE)

$(PYPROJECT): $(MSGPACT_DEP_VERSION_FILE)
	poetry run python dependency.py
	poetry lock
	poetry install

dep:
	cd ../../lib/py && make

