//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

package io.github.telepact.internal.validation;

import static io.github.telepact.internal.validation.MapValidationFailuresToInvalidFieldCases.mapValidationFailuresToInvalidFieldCases;

import java.util.List;

import io.github.telepact.TelepactError;
import io.github.telepact.internal.types.VUnion;

public class ValidateResult {
    public static void validateResult(VUnion resultUnionType, Object errorResult) {
        final var newErrorResultValidationFailures = resultUnionType.validate(
                errorResult, List.of(), new ValidateContext(null, null));
        if (!newErrorResultValidationFailures.isEmpty()) {
            throw new TelepactError(
                    "Failed internal telepact validation: "
                            + mapValidationFailuresToInvalidFieldCases(newErrorResultValidationFailures));
        }
    }
}
