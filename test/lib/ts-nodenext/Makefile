#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

LIB_TAR_GZ := ../../../lib/ts/dist-tgz/*.tgz
TAR_GZ := telepact.tgz
CLI := ../../../tool/telepact

all: codegen $(TAR_GZ)
	npm uninstall telepact || echo "no-op"
	npm install --ignore-scripts ./telepact.tgz
	npm install --ignore-scripts
	npm run build

$(TAR_GZ): dep
	cp $(LIB_TAR_GZ) telepact.tgz

dep:
	$(MAKE) -C ../../../lib/ts

codegen:
	$(CLI) codegen --schema-dir ../../../example/ts-codegen/api --lang ts --out src/gen

clean:
	rm -f telepact.tgz
	rm -rf src/gen
	rm -rf node_modules
	rm -f package-lock.json
