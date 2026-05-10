SHELL := /bin/bash

ROOT := /home/runner/work/telepact/telepact
NATS_URL ?= nats://demo.nats.io:4222
WARMUP ?= 5
ITERATIONS ?= 20
PYTHON := python3

.PHONY: prepare prepare-python prepare-typescript prepare-java run clean

prepare: prepare-python prepare-typescript prepare-java

prepare-python:
cd $(ROOT)/lib/py && $(MAKE)
cd $(ROOT)/test/performance/python && uv sync --all-groups
cd $(ROOT)/test/performance/python && uv pip install --python .venv/bin/python $(ROOT)/lib/py/dist/*.tar.gz

prepare-typescript:
cd $(ROOT)/lib/ts && $(MAKE)
cd $(ROOT)/test/performance/typescript && cp $(ROOT)/lib/ts/dist-tgz/*.tgz telepact.tgz
	cd $(ROOT)/test/performance/typescript && npm install --ignore-scripts
	cd $(ROOT)/test/performance/typescript && npm run build

prepare-java:
cd $(ROOT)/lib/java && $(MAKE)
cd $(ROOT)/test/performance/java && mvn install:install-file -Dfile=$(ROOT)/lib/java/target/telepact-$$(cat $(ROOT)/VERSION.txt).jar -DgroupId=io.github.telepact -DartifactId=telepact -Dversion=1.0 -Dpackaging=jar -q
cd $(ROOT)/test/performance/java && mvn -q -DskipTests compile dependency:copy-dependencies

run: prepare
cd $(ROOT)/test/performance && $(PYTHON) run.py --nats-url $(NATS_URL) --warmup $(WARMUP) --iterations $(ITERATIONS)

clean:
rm -f $(ROOT)/test/performance/results/raw-*.json
rm -f $(ROOT)/test/performance/results/latest-summary.json
rm -f $(ROOT)/test/performance/results/latest-summary.md
rm -rf $(ROOT)/test/performance/python/.venv $(ROOT)/test/performance/python/uv.lock
rm -rf $(ROOT)/test/performance/typescript/node_modules $(ROOT)/test/performance/typescript/dist
rm -rf $(ROOT)/test/performance/java/target
