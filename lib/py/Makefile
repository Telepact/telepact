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
	cp ../../LICENSE ../../NOTICE ./

	rm -rf dist
	poetry install

	# TODO: Get "include" to work in pyproject.toml
	telepact-project gitignore --remove telepact/json
	poetry build
	telepact-project gitignore --add telepact/json

clean:
	rm -rf dist
	rm -rf telepact/json
	rm -f ./LICENSE ./NOTICE
	poetry env remove --all

deploy: $(TAR_GZ)
	poetry publish
