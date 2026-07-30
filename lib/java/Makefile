#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

SHELL := /bin/bash

MVN_BUILD ?= install
SRC_FILES := $(shell find src -type f)
COMMON_SCHEMA_FILES := $(shell find ../../common -type f \( -name '*.json' -o -name '*.yaml' \))
JAR_FILE := target/telepact-$(shell cat ../../VERSION.txt).jar

$(JAR_FILE): $(SRC_FILES) $(COMMON_SCHEMA_FILES)
	mkdir -p src/main/resources
	ruby ../../tool/render_common_schema_json.rb ../../common src/main/resources
	cp ../../LICENSE ../../NOTICE src/main/resources
	
	mvn $(MVN_BUILD) -s settings.xml | grep -v "from central"; if [ $${PIPESTATUS[0]} -ne 0 ]; then exit 1; fi
	
clean:
	rm -rf src/main/resources
	rm -rf target
	rm -rf .m2

deploy: $(JAR_FILE)
	mvn -P credentialed deploy -s settings.xml -Ddeploy.skipUpload=false
