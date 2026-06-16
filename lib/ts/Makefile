#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

NPM_INSTALL ?= install --ignore-scripts
SRC_FILES := $(shell find src -type f)
BUILD_FILES := package.json package-lock.json tsconfig.json rollup.config.js
COMMON_SCHEMA_FILES := $(shell find ../../common -type f \( -name '*.json' -o -name '*.yaml' \))
TAR_GZ := dist-tgz/*.tgz

.PHONY: clean

$(TAR_GZ): $(SRC_FILES) $(BUILD_FILES) $(COMMON_SCHEMA_FILES)
	rm -rf inc
	mkdir -p inc
	ruby ../../tool/render_common_schema_json.rb ../../common inc

	rm -rf dist
	mkdir -p dist
	cp ../../LICENSE ../../NOTICE dist

	rm -rf dist-tgz
	mkdir -p dist-tgz

	npm $(NPM_INSTALL)
	npm run build
	npm pack --pack-destination ./dist-tgz

clean:
	rm -rf inc
	rm -rf dist
	rm -rf dist-tgz
	rm -rf node_modules
	rm -f dist/LICENSE dist/NOTICE

deploy: $(TAR_GZ)
	npm publish
