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

.PHONY: all clean

SRC_FILES := $(shell find telepact -type f)
TAR_GZ := dist/*.tar.gz

$(TAR_GZ): $(SRC_FILES)
	mkdir -p telepact/json
	cp ../../common/*.json telepact/json
	cp ../../LICENSE ../../NOTICE telepact/
	
	rm -rf dist
	poetry install
	poetry build

clean:
	rm -rf dist
	rm -rf telepact/json
	rm -f telepact/LICENSE telepact/NOTICE
	poetry env remove --all