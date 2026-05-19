#!/usr/bin/env bash

#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

set -euo pipefail

# The devcontainer intentionally provisions only Astral uv.
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh -o /tmp/uv-installer.sh
  env UV_UNMANAGED_INSTALL="/usr/local/bin" sh /tmp/uv-installer.sh
  rm -f /tmp/uv-installer.sh
fi
