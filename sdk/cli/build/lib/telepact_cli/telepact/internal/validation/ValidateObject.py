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

from typing import TYPE_CHECKING

from ..types.TObject import _OBJECT_NAME
from ...internal.validation.ValidationFailure import ValidationFailure

if TYPE_CHECKING:
    from ...internal.validation.ValidateContext import ValidateContext
    from ..types.TTypeDeclaration import TTypeDeclaration


def validate_object(value: object,
                    type_parameters: list['TTypeDeclaration'], ctx: 'ValidateContext') -> list['ValidationFailure']:
    from ...internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure

    if isinstance(value, dict):
        nested_type_declaration = type_parameters[0]

        validation_failures = []
        for k, v in value.items():
            ctx.path.append("*")

            nested_validation_failures = nested_type_declaration.validate(
                v, ctx)
            
            ctx.path.pop()

            nested_validation_failures_with_path = []
            for f in nested_validation_failures:
                this_path = [k] + f.path

                nested_validation_failures_with_path.append(
                    ValidationFailure(this_path, f.reason, f.data))

            validation_failures.extend(nested_validation_failures_with_path)

        return validation_failures
    else:
        return get_type_unexpected_validation_failure([], value, _OBJECT_NAME)
