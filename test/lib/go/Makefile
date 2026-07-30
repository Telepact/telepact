#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

SHELL := /bin/bash

BIN := bin/telepact-go-dispatcher
GO_SOURCES := $(shell find cmd -type f -name '*.go') $(shell find internal -type f -name '*.go' 2>/dev/null)
CODEGEN_DIR := cmd/dispatcher/gen
CLI := ../../../tool/telepact

all: codegen build

build: $(BIN)

$(BIN): go.mod go.sum $(GO_SOURCES)
	mkdir -p bin
	GO111MODULE=on go build -o $(BIN) ./cmd/dispatcher

codegen:
	rm -rf $(CODEGEN_DIR)
	mkdir -p $(CODEGEN_DIR)
	$(CLI) codegen --schema-dir ../../runner/schema/example --lang go --out $(CODEGEN_DIR) --package gen
	gofmt -w $(CODEGEN_DIR)

mod-tidy:
	GO111MODULE=on go mod tidy

run:
	GO111MODULE=on go run ./cmd/dispatcher

test-server: codegen
	GO111MODULE=on go run ./cmd/dispatcher

clean:
	rm -rf bin
	rm -f metrics.txt
	rm -rf $(CODEGEN_DIR)

.PHONY: all build codegen mod-tidy run test-server clean
