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

from typing import TYPE_CHECKING, cast
from ..types.TUnion import _UNION_NAME
from ...internal.validation.ValidationFailure import ValidationFailure

if TYPE_CHECKING:
    from ...internal.validation.ValidateContext import ValidateContext
    from ..types.TStruct import TStruct
    from ..types.TTypeDeclaration import TTypeDeclaration


def validate_union(value: object,
                   name: str, tags: dict[str, 'TStruct'], ctx: 'ValidateContext') -> list['ValidationFailure']:
    from ...internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure
    from ...internal.validation.ValidateUnionTags import validate_union_tags

    if isinstance(value, dict):
        selected_tags: dict[str, object]
        if name.startswith("fn."):
            selected_tags = {name: ctx.select.get(
                name) if ctx.select else None}
        else:
            selected_tags = cast(
                dict[str, object], ctx.select.get(name) if ctx.select else None)
        return validate_union_tags(tags, selected_tags, value, ctx)
    else:
        return get_type_unexpected_validation_failure([], value, _UNION_NAME)
