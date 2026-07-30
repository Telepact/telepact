//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.types;

import static io.github.telepact.internal.generation.GenerateRandomMockCall.generateRandomMockCall;
import static io.github.telepact.internal.validation.ValidateMockCall.validateMockCall;

import java.util.List;
import java.util.Map;

import io.github.telepact.internal.generation.GenerateContext;
import io.github.telepact.internal.validation.ValidateContext;
import io.github.telepact.internal.validation.ValidationFailure;

public class TMockCall implements TType {

    public static final String _MOCK_CALL_NAME = "_ext.Call_";

    public final Map<String, TType> types;

    public TMockCall(Map<String, TType> types) {
        this.types = types;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object givenObj,
            List<TTypeDeclaration> typeParameters, ValidateContext ctx) {
        return validateMockCall(givenObj, typeParameters, this.types, ctx);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            List<TTypeDeclaration> typeParameters, GenerateContext ctx) {
        return generateRandomMockCall(this.types, ctx);
    }

    @Override
    public String getName(ValidateContext ctx) {
        return _MOCK_CALL_NAME;
    }

}
