#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

SHELL := /bin/bash

VERSION := $(shell cat ../../VERSION.txt)
MODULE_PATH := github.com/telepact/telepact/lib/go

GO_SOURCES := $(shell find . -type f -name '*.go' -not -path './target/*')

SCHEMA_SOURCE_DIR := ../../common
SCHEMA_TARGET_DIR := internal/schema/do_not_edit

.PHONY: all build test fmt tidy clean deploy sync-schema-assets copy-common-assets

all: build

copy-common-assets:
	@mkdir -p $(SCHEMA_TARGET_DIR)
	ruby ../../tool/render_common_schema_json.rb $(SCHEMA_SOURCE_DIR) $(SCHEMA_TARGET_DIR)

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
