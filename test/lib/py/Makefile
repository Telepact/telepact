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

all: dep
	cp ../../../lib/py/dist/*.tar.gz telepact.tar.gz

	poetry lock
	poetry remove telepact || echo "no-op"
	poetry add ./telepact.tar.gz
	poetry install

	telepact codegen --schema-dir ../../runner/schema/example --lang py --out telepact_test/gen

dep:
	cd ../../../lib/py && make

test-server:
	poetry run python -m telepact_test

clean:
	rm -f telepact.tar.gz
	rm -rf telepact_test/gen
	rm -rf telepact_test/__pycache__
	rm -f poetry.lock
	poetry env remove --all
