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

VERSION := $(shell cat ../../VERSION.txt)

LIB_TAR_GZ := ../../sdk/console/dist-docker/*.tar.gz
TAR_GZ := telepact-console.tar.gz

all: $(TAR_GZ)
	npm install

	docker load < $(TAR_GZ)

	docker build --progress=plain --no-cache -f Dockerfile -t telepact-console-self-host:${VERSION} --build-arg TELEPACT_VERSION=${VERSION} .


$(TAR_GZ):
	cp $(LIB_TAR_GZ) $(TAR_GZ)

clean:
	rm -rf node_modules
	rm -f package-lock.json
	rm $(TAR_GZ)

test:
	npm run test