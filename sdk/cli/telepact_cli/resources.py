#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from importlib import resources as importlib_resources
import json
import yaml


def load_calculator_telepact_json() -> str:
    calculator_schema = importlib_resources.files('telepact_cli').joinpath('calculator.telepact.yaml').read_text()
    return json.dumps(yaml.safe_load(calculator_schema), separators=(',', ':'))
