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

GO_SOURCES := $(shell find . -type f -name '*.go' -not -path './target/*')

.PHONY: all build test fmt tidy clean

all: build

build: go.mod go.sum $(GO_SOURCES)
	GO111MODULE=on go build ./...

test:
	GO111MODULE=on go test ./...

fmt:
	gofmt -w $(GO_SOURCES)

tidy:
	GO111MODULE=on go mod tidy

clean:
	GO111MODULE=on go clean ./...
