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

all: dep codegen
	npm install
	npm run build

dep:
	cd ../../../lib/ts && make

codegen:
	telepact codegen --schema-dir ../../runner/schema/example --lang ts --out src/gen

test-server:
	npm start

clean:
	rm -rf src/gen
	rm -rf dist
	rm -rf node_modules
	rm -f package-lock.json
	cd ../../../lib/ts && make clean
