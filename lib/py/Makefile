SRC_FILES = $(shell find uapi -name '*.py')
PYPROJECT_FILE = pyproject.toml
JSON_FILES = $(shell find uapi -name '*.uapi.json')
COMMON_JSON_FILES = $(shell find ../../common -name '*.uapi.json')

.PHONY: all

all: $(PYPROJECT_FILE)

$(PYPROJECT_FILE): $(SRC_FILES) $(JSON_FILES)
	@bump-patch-version || (echo "Install bump-patch-version with 'pipx install ../../tool/bump_patch_version'" && exit 1)

$(JSON_FILES): $(COMMON_JSON_FILES)
	cp ../../common/*.uapi.json uapi