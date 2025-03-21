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

import static io.github.telepact.internal.types.GetType.getType;

import java.util.List;
import java.util.Map;
import java.util.TreeMap;

public class GetTypeUnexpectedValidationFailure {
        static List<ValidationFailure> getTypeUnexpectedValidationFailure(List<Object> path, Object value,
                        String expectedType) {
                final var actualType = getType(value);
                final Map<String, Object> data = new TreeMap<>(
                                Map.ofEntries(Map.entry("actual", Map.of(actualType, Map.of())),
                                                Map.entry("expected", Map.of(expectedType, Map.of()))));
                return List.of(
                                new ValidationFailure(path, "TypeUnexpected", data));
        }
}
