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

import static io.github.telepact.internal.generation.GenerateRandomValueOfType.generateRandomValueOfType;
import static io.github.telepact.internal.validation.ValidateValueOfType.validateValueOfType;

import java.util.List;
import java.util.Map;

import io.github.telepact.internal.generation.GenerateContext;
import io.github.telepact.internal.validation.ValidateContext;
import io.github.telepact.internal.validation.ValidationFailure;

public class VTypeDeclaration {
    public final VType type;
    public final boolean nullable;
    public final List<VTypeDeclaration> typeParameters;

    public VTypeDeclaration(
            VType type,
            boolean nullable, List<VTypeDeclaration> typeParameters) {
        this.type = type;
        this.nullable = nullable;
        this.typeParameters = typeParameters;
    }

    public List<ValidationFailure> validate(Object value, ValidateContext ctx) {
        return validateValueOfType(value, this.type, this.nullable, this.typeParameters, ctx);
    }

    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            GenerateContext ctx) {
        return generateRandomValueOfType(blueprintValue, useBlueprintValue, this.type, this.nullable,
                this.typeParameters, ctx);
    }
}
