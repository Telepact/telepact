package io.github.msgpact.internal.types;

import static io.github.msgpact.internal.generation.GenerateRandomUMockCall.generateRandomUMockCall;
import static io.github.msgpact.internal.validation.ValidateMockCall.validateMockCall;

import java.util.List;
import java.util.Map;

import io.github.msgpact.internal.generation.GenerateContext;
import io.github.msgpact.internal.validation.ValidateContext;
import io.github.msgpact.internal.validation.ValidationFailure;

public class VMockCall implements VType {

    public static final String _MOCK_CALL_NAME = "_ext.Call_";

    public final Map<String, VType> types;

    public VMockCall(Map<String, VType> types) {
        this.types = types;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object givenObj,
            List<VTypeDeclaration> typeParameters, ValidateContext ctx) {
        return validateMockCall(givenObj, typeParameters, this.types, ctx);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            List<VTypeDeclaration> typeParameters, GenerateContext ctx) {
        return generateRandomUMockCall(this.types, ctx);
    }

    @Override
    public String getName() {
        return _MOCK_CALL_NAME;
    }

}
