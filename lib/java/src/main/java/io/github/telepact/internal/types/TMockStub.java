//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.types;

import static io.github.telepact.internal.generation.GenerateRandomMockStub.generateRandomMockStub;
import static io.github.telepact.internal.validation.ValidateMockStub.validateMockStub;

import java.util.List;
import java.util.Map;

import io.github.telepact.internal.generation.GenerateContext;
import io.github.telepact.internal.validation.ValidateContext;
import io.github.telepact.internal.validation.ValidationFailure;

public class TMockStub implements TType {

    static final String _MOCK_STUB_NAME = "_ext.Stub_";

    public final Map<String, TType> types;

    public TMockStub(Map<String, TType> types) {
        this.types = types;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object givenObj,
            List<TTypeDeclaration> typeParameters, ValidateContext ctx) {
        return validateMockStub(givenObj, typeParameters, this.types, ctx);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            List<TTypeDeclaration> typeParameters, GenerateContext ctx) {
        return generateRandomMockStub(this.types, ctx);
    }

    @Override
    public String getName(ValidateContext ctx) {
        return _MOCK_STUB_NAME;
    }

}
