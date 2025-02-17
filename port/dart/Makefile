SRC_FILES = $(shell find lib -name '*.dart')
PUBSPEC_FILE = pubspec.yaml

.PHONY: all

all: $(PUBSPEC_FILE)
	cp ../../LICENSE ../../NOTICE ./
	npm install
	
	npx rollup -c rollup.crc32.config.js
	npx rollup -c rollup.msgpackr.config.js

	cp node_modules/uapi/dist/index.iife.js lib/js/uapi.js
	cp dist/crc32.iife.js lib/js/crc32.js
	cp dist/msgpackr.iife.js lib/js/msgpackr.js	

	dart analyze

$(PUBSPEC_FILE): $(SRC_FILES)
	uapi-version bump || (echo "Install uapi-version bump with 'pipx install ../../tool/uapi_version'" && exit 1)
