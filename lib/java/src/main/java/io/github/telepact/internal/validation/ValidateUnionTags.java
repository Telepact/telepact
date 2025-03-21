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

import static io.github.telepact.internal.validation.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;
import static io.github.telepact.internal.validation.ValidateUnionStruct.validateUnionStruct;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;

import io.github.telepact.internal.types.VStruct;

public class ValidateUnionTags {
    static List<ValidationFailure> validateUnionTags(
            Map<String, VStruct> referenceTags, Map<String, Object> selectedTags,
            Map<?, ?> actual, ValidateContext ctx) {
        if (actual.size() != 1) {
            return List.of(
                    new ValidationFailure(new ArrayList<Object>(),
                            "ObjectSizeUnexpected", Map.of("actual", actual.size(), "expected", 1)));
        }

        final var entry = ((Map<String, Object>) actual).entrySet().stream().findAny().get();
        final var unionTarget = (String) entry.getKey();
        final var unionPayload = entry.getValue();

        final var referenceStruct = referenceTags.get(unionTarget);
        if (referenceStruct == null) {
            return Collections
                    .singletonList(new ValidationFailure(List.of(unionTarget),
                            "ObjectKeyDisallowed", Map.of()));
        }

        if (unionPayload instanceof Map<?, ?> m2) {
            final var nestedValidationFailures = validateUnionStruct(referenceStruct, unionTarget,
                    (Map<String, Object>) m2, selectedTags, ctx);

            final var nestedValidationFailuresWithPath = new ArrayList<ValidationFailure>();
            for (final var f : nestedValidationFailures) {
                final List<Object> thisPath = new ArrayList<>(f.path);
                thisPath.add(0, unionTarget);

                nestedValidationFailuresWithPath.add(new ValidationFailure(thisPath, f.reason, f.data));
            }

            return nestedValidationFailuresWithPath;
        } else {
            return getTypeUnexpectedValidationFailure(List.of(unionTarget),
                    unionPayload, "Object");
        }
    }
}
