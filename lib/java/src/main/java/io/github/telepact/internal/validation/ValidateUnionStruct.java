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
