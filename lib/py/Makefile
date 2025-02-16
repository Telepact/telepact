SRC_FILES = $(shell find uapi -name '*.py')
PYPROJECT_FILE = pyproject.toml

.PHONY: all

all: $(PYPROJECT_FILE)
	cp ../../common/*.json uapi
	cp ../../LICENSE ../../NOTICE uapi
	poetry install
	poetry build

$(PYPROJECT_FILE): $(SRC_FILES)
	@uapi-version bump || (echo "Install uapi-version bump with 'pipx install ../../tool/uapi_version'" && exit 1)

