#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

LIB_TAR_GZ := ../../../lib/py/dist/*.tar.gz
TAR_GZ := telepact.tar.gz

all: codegen $(TAR_GZ)
	uv sync --all-groups
	uv pip install --python .venv/bin/python ./telepact.tar.gz

$(TAR_GZ): dep
	cp $(LIB_TAR_GZ) telepact.tar.gz

dep:
	$(MAKE) -C ../../../lib/py

codegen:
	telepact codegen --schema-dir ../../runner/schema/example --lang py --out telepact_test/gen

test-server:
	uv run python -m telepact_test

clean:
	rm -f telepact.tar.gz
	rm -rf telepact_test/gen
	rm -rf telepact_test/__pycache__
	rm -f uv.lock
	rm -rf .venv
