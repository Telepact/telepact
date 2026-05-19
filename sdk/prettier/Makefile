#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

NPM_INSTALL ?= install --ignore-scripts
TAR_GZ := dist-tgz/*.tgz

.PHONY: clean test deploy

$(TAR_GZ):
	rm -rf dist
	mkdir -p dist
	cp ../../LICENSE ../../NOTICE dist

	mkdir -p dist-tgz

	npm $(NPM_INSTALL)
	npm run build
	npm pack --pack-destination ./dist-tgz

clean:
	rm -rf dist
	rm -rf dist-tgz
	rm -rf node_modules

test:
	npm test

deploy: $(TAR_GZ)
	npm publish
