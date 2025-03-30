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

import static io.github.telepact.internal.types.TBytes._BYTES_NAME;

import java.util.Base64;
import java.util.List;
import java.util.Map;

public class ValidateBytes {

    public static List<ValidationFailure> validateBytes(Object value, ValidateContext ctx) {
        if (value instanceof byte[]) {
            if (ctx.coerceBase64) {
                setCoercedPath(ctx.path, ctx.base64Coercions);
            }
            return List.of();
        } else if (value instanceof String) {
            try {
                Base64.getDecoder().decode((String) value);
                if (!ctx.coerceBase64) {
                    setCoercedPath(ctx.path, ctx.bytesCoercions);
                }
                return List.of();
            } catch (IllegalArgumentException e) {
                return GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure(
                    List.of(), value, "Base64String"
                );
            }
        } else {
            return GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure(
                List.of(), value, _BYTES_NAME
            );
        }
    }

    private static void setCoercedPath(List<String> path, Map<String, Object> coercedPath) {
        String part = path.get(0);

        if (path.size() > 1) {
            coercedPath.putIfAbsent(part, new java.util.HashMap<String, Object>());
            setCoercedPath(path.subList(1, path.size()), (Map<String, Object>) coercedPath.get(part));
        } else {
            coercedPath.put(part, true);
        }
    }
}