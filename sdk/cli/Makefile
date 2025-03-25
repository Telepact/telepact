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

.PHONY: all dep clean

all: dep
	cp ../../LICENSE ../../NOTICE telepact_cli
	rm -rf tmp
	mkdir -p tmp
	tar -xzvf ../../lib/py/dist/*.tar.gz -C tmp
	rm -rf telepact_cli/telepact
	mv tmp/*/telepact telepact_cli/telepact
	rm -rf tmp

	rm -rf dist
	poetry lock
	poetry install
	poetry build

dep:
	$(MAKE) -C ../../lib/py

clean:
	rm -rf dist
	rm -rf telepact_cli/telepact
	rm -rf tmp
	rm -f telepact_cli/LICENSE telepact_cli/NOTICE
	poetry env remove --all

test:
	poetry run telepact codegen --schema-dir tests/data --lang java --out tests/output/java --package output
	poetry run telepact codegen --schema-dir tests/data --lang py --out tests/output/py
	poetry run telepact codegen --schema-dir tests/data --lang ts --out tests/output/ts