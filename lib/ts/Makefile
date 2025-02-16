SRC_FILES = $(shell find src -name '*.ts')
PACKAGE_JSON_FILE = package.json

.PHONY: all

all: $(PACKAGE_JSON_FILE)
	mkdir -p inc
	cp ../../common/*.json inc
	mkdir -p dist
	cp ../../LICENSE ../../NOTICE dist
	npm install
	npm run build

$(PACKAGE_JSON_FILE): $(SRC_FILES)
	uapi-version bump || (echo "Install uapi-version bump with 'pipx install ../../tool/uapi_version'" && exit 1)
