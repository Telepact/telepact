#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

.PHONY: all clean

all:
	uv sync
	uv build

clean:
	rm -rf dist
	rm -rf .venv
	rm -f uv.lock