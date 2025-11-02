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

VERSION := $(shell cat ../../VERSION.txt)
MODULE_PATH := github.com/telepact/telepact/lib/go

GO_SOURCES := $(shell find . -type f -name '*.go' -not -path './target/*')

SCHEMA_SOURCE_DIR := ../../common
SCHEMA_TARGET_DIR := internal/schema/do_not_edit
SCHEMA_SOURCE_FILES := $(notdir $(wildcard $(SCHEMA_SOURCE_DIR)/*.json))
SCHEMA_TARGETS := $(addprefix $(SCHEMA_TARGET_DIR)/,$(SCHEMA_SOURCE_FILES))

.PHONY: all build test fmt tidy clean deploy sync-schema-assets copy-common-assets

all: build

copy-common-assets:
	@mkdir -p $(SCHEMA_TARGET_DIR)
	cp $(SCHEMA_SOURCE_DIR)/*.json $(SCHEMA_TARGET_DIR)/

sync-schema-assets:
	@$(MAKE) copy-common-assets
	@if [ -n "$$(git status --porcelain $(SCHEMA_TARGET_DIR))" ]; then \
		echo "ERROR: Schema assets updated. Please run 'make go' and commit the changes."; \
		exit 1; \
	fi

build: sync-schema-assets go.mod go.sum $(GO_SOURCES)
	GO111MODULE=on go build ./...

fmt:
	gofmt -w $(GO_SOURCES)

tidy:
	GO111MODULE=on go mod tidy

clean:
	GO111MODULE=on go clean ./...

deploy: build
	GO111MODULE=on GOPROXY=proxy.golang.org,direct go list -m $(MODULE_PATH)@v$(VERSION)
