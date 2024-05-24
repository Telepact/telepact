package io.github.brenbar.uapi.internal.types;

import java.util.List;
import java.util.Map;

import io.github.brenbar.uapi.RandomGenerator;
import io.github.brenbar.uapi.internal.validation.ValidationFailure;

import static io.github.brenbar.uapi.internal.generation.GenerateRandomInteger.generateRandomInteger;
import static io.github.brenbar.uapi.internal.validation.ValidateInteger.validateInteger;

public class UInteger implements UType {
    public static final String _INTEGER_NAME = "Integer";

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, Map<String, Object> select, String fn,
            List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics) {
        return validateInteger(value);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics, RandomGenerator randomGenerator) {
        return generateRandomInteger(blueprintValue, useBlueprintValue, randomGenerator);
    }

    @Override
    public String getName(List<UTypeDeclaration> generics) {
        return _INTEGER_NAME;
    }
}
