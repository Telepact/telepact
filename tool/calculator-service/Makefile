PYPROJECT = pyproject.toml
UAPI_DEP_VERSION_FILE = ../../lib/py/VERSION.txt
SCHEMA_FILE = ../../qa/test/schema/calculator/calculator.uapi.json
COPIED_SCHEMA_FILE = calculator_service/calculator.uapi.json

.PHONY: all dep

all: dep $(PYPROJECT) $(COPIED_SCHEMA_FILE)

$(COPIED_SCHEMA_FILE): $(SCHEMA_FILE)
	cp $(SCHEMA_FILE) $(COPIED_SCHEMA_FILE)

$(PYPROJECT): $(UAPI_DEP_VERSION_FILE)
	poetry run python dependency.py
	poetry lock
	poetry install

dep:
	cd ../../lib/py && make

