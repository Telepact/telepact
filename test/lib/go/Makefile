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

BIN := bin/telepact-go-dispatcher
GO_SOURCES := $(shell find cmd -type f -name '*.go') $(shell find internal -type f -name '*.go' 2>/dev/null)

all: codegen build

build: $(BIN)

$(BIN): go.mod go.sum $(GO_SOURCES)
	mkdir -p bin
	GO111MODULE=on go build -o $(BIN) ./cmd/dispatcher

codegen:
	@echo "Go code generation is not yet automated; skipping"

mod-tidy:
	GO111MODULE=on go mod tidy

run:
	GO111MODULE=on go run ./cmd/dispatcher

test-server: codegen
	GO111MODULE=on go run ./cmd/dispatcher

clean:
	rm -rf bin
	rm -f metrics.txt

.PHONY: all build codegen mod-tidy run test-server clean
