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

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class ValidateSelect {

    public static List<ValidationFailure> validateSelect(Object givenObj,
            Map<String, Object> possibleFnSelects, ValidateContext ctx) {
        if (!(givenObj instanceof Map) || givenObj == null) {
            return GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure(new ArrayList<>(), givenObj,
                    "Object");
        }

        Map<String, Object> possibleSelect = (Map<String, Object>) possibleFnSelects.get(ctx.fn);

        return isSubSelect(new ArrayList<>(), givenObj, possibleSelect);
    }

    private static List<ValidationFailure> isSubSelect(List<Object> path, Object givenObj,
            Object possibleSelectSection) {

        if (possibleSelectSection instanceof List) {
            if (!(givenObj instanceof List)) {
                return GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure(path, givenObj, "Array");
            }

            List<ValidationFailure> validationFailures = new ArrayList<>();

            List<?> givenObjList = (List<?>) givenObj;
            List<?> possibleSelectList = (List<?>) possibleSelectSection;

            for (int index = 0; index < givenObjList.size(); index++) {
                Object element = givenObjList.get(index);
                if (!possibleSelectList.contains(element)) {
                    var loopPath = new ArrayList<>(path);
                    loopPath.add(index);
                    validationFailures.add(new ValidationFailure(loopPath, "ArrayElementDisallowed", Map.of()));
                }
            }

            return validationFailures;
        } else if (possibleSelectSection instanceof Map) {
            if (!(givenObj instanceof Map) || givenObj == null) {
                return GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure(path, givenObj, "Object");
            }

            List<ValidationFailure> validationFailures = new ArrayList<>();

            Map<String, Object> givenObjMap = (Map<String, Object>) givenObj;
            Map<String, Object> possibleSelectMap = (Map<String, Object>) possibleSelectSection;

            for (Map.Entry<String, Object> entry : givenObjMap.entrySet()) {
                String key = entry.getKey();
                Object value = entry.getValue();
                if (possibleSelectMap.containsKey(key)) {
                    var loopPath = new ArrayList<>(path);
                    loopPath.add(key);
                    List<ValidationFailure> innerFailures = isSubSelect(loopPath, value, possibleSelectMap.get(key));
                    validationFailures.addAll(innerFailures);
                } else {
                    validationFailures.add(new ValidationFailure(new ArrayList<>(path) {
                        {
                            add(key);
                        }
                    }, "ObjectKeyDisallowed", Map.of()));
                }
            }

            return validationFailures;
        }

        return new ArrayList<>();
    }
}
