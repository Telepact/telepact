#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from importlib import resources as importlib_resources
from ... import json


def get_internal_telepact_json() -> str:
    return importlib_resources.files(json).joinpath('internal.telepact.json').read_text()
