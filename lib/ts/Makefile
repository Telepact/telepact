SRC_FILES = $(shell find src -name '*.ts')
PACKAGE_JSON_FILE = package.json
JSON_FILES = $(shell find inc -name '*.uapi.json')
COMMON_JSON_FILES = $(shell find ../../common -name '*.uapi.json')

.PHONY: all

all: $(PACKAGE_JSON_FILE)

$(PACKAGE_JSON_FILE): $(SRC_FILES) $(JSON_FILES)
	bump-patch-version || (echo "Install bump-patch-version with 'pipx install ../../tool/bump_patch_version'" && exit 1)

$(JSON_FILES): $(COMMON_JSON_FILES)
	cp ../../common/*.uapi.json inc