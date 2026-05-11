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
ROOT := ../..
LIB_PY_TAR_GZ := $(ROOT)/lib/py/dist/*.tar.gz
LIB_TS_TAR_GZ := $(ROOT)/lib/ts/dist-tgz/*.tgz
LIB_JAVA_JAR := $(ROOT)/lib/java/target/telepact-$(shell cat $(ROOT)/VERSION.txt).jar
PY_TAR_GZ := telepact.tar.gz
TS_TAR_GZ := ts/telepact.tgz

all: setup

setup: $(PY_TAR_GZ) $(TS_TAR_GZ) python-deps python-proto ts-deps java-deps

$(PY_TAR_GZ):
$(MAKE) -C $(ROOT)/lib/py
cp $(LIB_PY_TAR_GZ) $(PY_TAR_GZ)

$(TS_TAR_GZ):
$(MAKE) -C $(ROOT)/lib/ts
cp $(LIB_TS_TAR_GZ) $(TS_TAR_GZ)

python-deps: $(PY_TAR_GZ)
uv sync --all-groups
uv pip install --python .venv/bin/python ./telepact.tar.gz

python-proto:
mkdir -p gen/py
protoc --proto_path=schema --python_out=gen/py schema/benchmark.proto


ts-deps: $(TS_TAR_GZ)
npm --prefix ts uninstall telepact || echo "no-op"
npm --prefix ts install --ignore-scripts ./telepact.tgz
npm --prefix ts install --ignore-scripts
npm --prefix ts run build

java-deps:
$(MAKE) -C $(ROOT)/lib/java
mkdir -p java/target/dep
cp $(LIB_JAVA_JAR) java/target/dep/telepact.jar
cd java && mvn install:install-file -Dfile=target/dep/telepact.jar -DgroupId=io.github.telepact -DartifactId=telepact -Dversion=1.0 -Dpackaging=jar -s settings.xml | grep -v "from central"; if [ $${PIPESTATUS[0]} -ne 0 ]; then exit 1; fi
cd java && mvn -q -s settings.xml -DskipTests compile

run: setup
uv run python run.py

clean:
rm -rf .venv
rm -rf gen
rm -rf output
rm -f telepact.tar.gz
rm -f ts/telepact.tgz
$(MAKE) -C ts clean
$(MAKE) -C java clean
