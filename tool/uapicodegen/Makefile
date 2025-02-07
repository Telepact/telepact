PYPROJECT = pyproject.toml
VERSION_FILE = VERSION.txt
SRC_FILES = $(shell find uapicodegen -name '*.py' -o -name '*.toml' -o -name '*.j2')
BUILD_DIR = dist
BUILD_MARKER = $(BUILD_DIR)/.built
DEP_VERSION_FILE = ../../lib/py/VERSION.txt

.PHONY: all build clean check dep

all: dep check build

build: $(BUILD_MARKER)

$(BUILD_MARKER): $(VERSION_FILE)
	poetry build --clean
	touch $(BUILD_MARKER)

$(VERSION_FILE): $(SRC_FILES) $(PYPROJECT)
	poetry run python version.py

$(PYPROJECT): $(DEP_VERSION_FILE)
	poetry lock
	poetry install

dep:
	cd ../../lib/py && make

clean:
	rm -rf dist/
	rm -f $(VERSION_FILE)
