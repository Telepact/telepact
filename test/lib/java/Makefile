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

.PHONY: all dep

all: dep
	rm -rf target
	mkdir -p target

	cp ../../../lib/java/target/*.jar target/telepact.jar
	mvn install:install-file -Dfile=target/telepact.jar -DgroupId=io.github.telepact -DartifactId=telepact -Dversion=1.0 -Dpackaging=jar

	telepact codegen --schema-dir ../../runner/schema/example --lang java --out src/gen/java/telepacttest --package telepacttest

dep:
	cd ../../../lib/java && make