SRC_FILES = $(shell find src -name '*.ts')
PACKAGE_JSON_FILE = package.json
JSON_FILES = $(shell find inc -name '*.uapi.json')
COMMON_JSON_FILES = $(shell find ../../common -name '*.uapi.json')

.PHONY: all

all: $(PACKAGE_JSON_FILE)

$(PACKAGE_JSON_FILE): $(SRC_FILES) $(JSON_FILES)
	uapi-version bump || (echo "Install uapi-version bump with 'pipx install ../../tool/uapi_version'" && exit 1)

$(JSON_FILES): $(COMMON_JSON_FILES)
	cp ../../common/*.uapi.json inc