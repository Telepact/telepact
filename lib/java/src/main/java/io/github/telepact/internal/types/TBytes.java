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

package io.github.telepact.internal.types;

import static io.github.telepact.internal.generation.GenerateRandomBytes.generateRandomBytes;
import static io.github.telepact.internal.validation.ValidateBytes.validateBytes;


import java.util.List;

import io.github.telepact.internal.generation.GenerateContext;
import io.github.telepact.internal.validation.ValidateContext;
import io.github.telepact.internal.validation.ValidationFailure;

public class TBytes implements TType {

    public static String getBytesName(ValidateContext ctx) {
        if (ctx.expectBytes) {
            return "Bytes";
        } else {
            return "Base64String";
        }
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<TTypeDeclaration> typeParameters, ValidateContext ctx) {
        return validateBytes(value, ctx);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            List<TTypeDeclaration> typeParameters, GenerateContext ctx) {
        return generateRandomBytes(blueprintValue, useBlueprintValue, ctx);
    }

    @Override
    public String getName(ValidateContext ctx) {
        return getBytesName(ctx);
    }

}
