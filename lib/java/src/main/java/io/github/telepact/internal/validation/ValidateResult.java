//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.validation;

import static io.github.telepact.internal.validation.MapValidationFailuresToInvalidFieldCases.mapValidationFailuresToInvalidFieldCases;

import java.util.List;

import io.github.telepact.TelepactError;
import io.github.telepact.internal.types.TUnion;

public class ValidateResult {
    public static void validateResult(TUnion resultUnionType, Object errorResult) {
        final var newErrorResultValidationFailures = resultUnionType.validate(
                errorResult, List.of(), new ValidateContext(null, null, false));
        if (!newErrorResultValidationFailures.isEmpty()) {
            throw new TelepactError(
                    "Failed internal telepact validation: "
                            + mapValidationFailuresToInvalidFieldCases(newErrorResultValidationFailures));
        }
    }
}
