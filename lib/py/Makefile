SRC_FILES = $(shell find uapi -name '*.py')
PYPROJECT_FILE = pyproject.toml
JSON_FILES = $(shell find uapi -name '*.uapi.json')
COMMON_JSON_FILES = $(shell find ../../common -name '*.uapi.json')

.PHONY: all

all: $(PYPROJECT_FILE)
	mkdir -p uapi/json
	cp ../../common/*.uapi.json uapi/json
	
	rm -rf dist
	poetry build

$(PYPROJECT_FILE): $(SRC_FILES)
	@uapi-version bump || (echo "Install uapi-version bump with 'pipx install ../../tool/uapi_version'" && exit 1)
