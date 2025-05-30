#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

SHELL := /bin/bash

MVN_BUILD ?= install
SRC_FILES := $(shell find src -type f)
JAR_FILE := target/telepact-$(shell cat ../../VERSION.txt).jar

$(JAR_FILE): $(SRC_FILES)
	mkdir -p src/main/resources
	cp ../../common/*.json src/main/resources
	cp ../../LICENSE ../../NOTICE src/main/resources
	
	mvn $(MVN_BUILD) -s settings.xml | grep -v "from central"
	@if [ $${PIPESTATUS[0]} -ne 0 ]; then exit 1; fi	

clean:
	rm -rf src/main/resources
	rm -rf target
	rm -rf .m2

deploy:
	mvn -P credentialed deploy -Ddeploy.skipUpload=false