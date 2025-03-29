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

.PHONY: all

all: dep
	cp ../cli/dist/telepact_cli-*.tar.gz telepact_cli.tar.gz
	
	docker build --progress=plain --no-cache -f Dockerfile -t telepact-mock:${VERSION} .

	mkdir -p dist

	docker save telepact-mock:${VERSION} | gzip > dist/telepact-mock-image-${VERSION}.tar.gz

dep:
	$(MAKE) -C ../cli

dev:
	docker-compose up --build

test:
	bash test.sh

clean:
	rm -f telepact_cli.tar.gz
	docker-compose rm -f
	docker rmi telepact-mock