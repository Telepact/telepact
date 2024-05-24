package io.github.brenbar.uapi.internal.types;

import static io.github.brenbar.uapi.internal.validation.ValidateMockCall.validateMockCall;

import java.util.List;
import java.util.Map;

import io.github.brenbar.uapi.RandomGenerator;
import io.github.brenbar.uapi.internal.validation.ValidationFailure;

public class UMockCall implements UType {

    public static final String _MOCK_CALL_NAME = "_ext.Call_";

    public final Map<String, UType> types;

    public UMockCall(Map<String, UType> types) {
        this.types = types;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object givenObj, Map<String, Object> select, String fn,
            List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics) {
        return validateMockCall(givenObj, select, fn, typeParameters, generics, this.types);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics,
            RandomGenerator randomGenerator) {
        throw new UnsupportedOperationException("Not implemented");
    }

    @Override
    public String getName(List<UTypeDeclaration> generics) {
        return _MOCK_CALL_NAME;
    }

}
