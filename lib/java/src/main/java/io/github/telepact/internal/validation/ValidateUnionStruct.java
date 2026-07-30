//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.validation;

import static io.github.telepact.internal.validation.ValidateStructFields.validateStructFields;

import java.util.List;
import java.util.Map;

import io.github.telepact.internal.types.TStruct;

public class ValidateUnionStruct {
    static List<ValidationFailure> validateUnionStruct(
            TStruct unionStruct,
            String unionTag,
            Map<String, Object> actual, Map<String, Object> selectedTags, ValidateContext ctx) {
        final var selectedFields = selectedTags == null ? null : (List<String>) selectedTags.get(unionTag);

        ctx.path.push(unionTag);

        final var result = validateStructFields(unionStruct.fields, selectedFields, actual, ctx);

        ctx.path.pop();

        return result;
    }
}
