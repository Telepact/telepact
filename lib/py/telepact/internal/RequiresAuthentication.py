#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ..TelepactSchema import TelepactSchema


def requires_authentication(telepact_schema: 'TelepactSchema', function_name: str) -> bool:
    function_definition = next(
        (
            cast(dict[str, object], definition)
            for definition in telepact_schema.full
            if isinstance(definition, dict) and function_name in definition
        ),
        None,
    )
    if function_name.endswith("_") or (
        isinstance(function_definition, dict)
        and function_definition.get("$internal") is True
    ):
        return False

    if "union.Auth_" not in telepact_schema.parsed:
        return False

    return not (
        isinstance(function_definition, dict)
        and function_definition.get("$authenticated") is False
    )
