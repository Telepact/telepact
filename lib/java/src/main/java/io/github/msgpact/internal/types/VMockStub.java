package io.github.msgpact.internal.types;

import static io.github.msgpact.internal.generation.GenerateRandomUMockStub.generateRandomUMockStub;
import static io.github.msgpact.internal.validation.ValidateMockStub.validateMockStub;

import java.util.List;
import java.util.Map;

import io.github.msgpact.internal.generation.GenerateContext;
import io.github.msgpact.internal.validation.ValidateContext;
import io.github.msgpact.internal.validation.ValidationFailure;

public class VMockStub implements VType {

    static final String _MOCK_STUB_NAME = "_ext.Stub_";

    public final Map<String, VType> types;

    public VMockStub(Map<String, VType> types) {
        this.types = types;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object givenObj,
            List<VTypeDeclaration> typeParameters, ValidateContext ctx) {
        return validateMockStub(givenObj, typeParameters, this.types, ctx);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            List<VTypeDeclaration> typeParameters, GenerateContext ctx) {
        return generateRandomUMockStub(this.types, ctx);
    }

    @Override
    public String getName() {
        return _MOCK_STUB_NAME;
    }

}
