#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

.PHONY: all clean

SRC_FILES := $(shell find telepact -type f)
COMMON_SCHEMA_FILES := $(shell find ../../common -type f \( -name '*.json' -o -name '*.yaml' \))
TAR_GZ := dist/*.tar.gz

$(TAR_GZ): $(SRC_FILES) $(COMMON_SCHEMA_FILES)
	rm -rf telepact/json
	mkdir -p telepact/json
	ruby ../../tool/render_common_schema_json.rb ../../common telepact/json
	cp ../../LICENSE ../../NOTICE ./

	rm -rf dist
	uv sync --all-groups
	uv build

clean:
	rm -rf dist
	rm -rf telepact/json
	rm -f ./LICENSE ./NOTICE
	rm -rf .venv
	rm -f uv.lock

deploy: $(TAR_GZ)
	uv publish
