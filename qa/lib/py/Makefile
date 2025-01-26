PYPROJECT = pyproject.toml
VERSION_FILE = VERSION.txt
SRC_FILES = $(shell find uapicodegen -name '*.py' -o -name '*.toml' -o -name '*.j2')
BUILD_DIR = dist
BUILD_MARKER = $(BUILD_DIR)/.built
UAPI_DEP_VERSION_FILE = ../../../lib/py/VERSION.txt
CODEGEN_DEP_VERSION_FILE = ../../../tool/uapicodegen/VERSION.txt

.PHONY: all dep

all: dep $(PYPROJECT)

$(PYPROJECT): $(UAPI_DEP_VERSION_FILE) $(CODEGEN_DEP_VERSION_FILE)
	poetry run python dependency.py
	poetry lock
	poetry install

dep:
	cd ../../../lib/py && make
	cd ../../../tool/uapicodegen && make

