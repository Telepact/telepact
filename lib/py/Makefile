PYPROJECT = pyproject.toml
VERSION_FILE = VERSION.txt
SRC_FILES = $(shell find uapi -name '*.py' -o -name '*.toml' -o -name '*.json')
BUILD_DIR = dist
BUILD_MARKER = $(BUILD_DIR)/.built

.PHONY: all build clean

all: build

build: $(BUILD_MARKER)

$(BUILD_MARKER): $(VERSION_FILE)
	poetry build --clean
	touch $(BUILD_MARKER)

$(VERSION_FILE): $(SRC_FILES)
	poetry run python version.py

clean:
	rm -rf dist/
	rm -f $(VERSION_FILE)
