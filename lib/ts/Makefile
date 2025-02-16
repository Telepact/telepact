SRC_FILES = $(shell find src -name '*.ts')
PACKAGE_JSON_FILE = package.json
JSON_FILES = $(shell find inc -name '*.json')
COMMON_JSON_FILES = $(shell find ../../common -name '*.json')

.PHONY: all

all: $(PACKAGE_JSON_FILE)
	npm install
	npm run build

$(PACKAGE_JSON_FILE): $(SRC_FILES) $(JSON_FILES)
	uapi-version bump || (echo "Install uapi-version bump with 'pipx install ../../tool/uapi_version'" && exit 1)

$(JSON_FILES): $(COMMON_JSON_FILES)
	mkdir -p inc
	cp ../../common/*.json inc
	mkdir -p dist
	cp ../../LICENSE ../../NOTICE dist
