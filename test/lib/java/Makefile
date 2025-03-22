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

LIB_JAR := target/telepact.jar
TARGET_JAR := target/telepacttest-1.0-SNAPSHOT.jar

$(TARGET_JAR): codegen $(LIB_JAR)
	mvn install:install-file -Dfile=target/dep/telepact.jar -DgroupId=io.github.telepact -DartifactId=telepact -Dversion=1.0 -Dpackaging=jar -s settings.xml | grep -v "from central"
	mvn package -DskipTests -s settings.xml | grep -v "from central"

$(LIB_JAR): dep
	mkdir -p target/dep
	cp $(shell find ../../../lib/java/target -name "*.jar" -not -name "*javadoc.jar" -not -name "*sources.jar") target/dep/telepact.jar

dep:
	cd ../../../lib/java && make

codegen:
	telepact codegen --schema-dir ../../runner/schema/example --lang java --out src/gen/java/telepacttest --package telepacttest

test-server:
	mvn verify -s settings.xml | grep -v "from central"

clean:
	rm -rf target
	rm -rf .m2