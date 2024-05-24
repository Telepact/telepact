package io.github.brenbar.uapi.internal.types;

import java.util.List;
import java.util.Map;

import io.github.brenbar.uapi.RandomGenerator;
import io.github.brenbar.uapi.internal.ValidationFailure;

import static io.github.brenbar.uapi.internal.ValidateString.validateString;
import static io.github.brenbar.uapi.internal.GenerateRandomString.generateRandomString;

public class UString implements UType {
    public static final String _STRING_NAME = "String";

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, Map<String, Object> select, String fn,
            List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics) {
        return validateString(value);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics,
            RandomGenerator randomGenerator) {
        return generateRandomString(blueprintValue, useBlueprintValue, randomGenerator);
    }

    @Override
    public String getName(List<UTypeDeclaration> generics) {
        return _STRING_NAME;
    }
}