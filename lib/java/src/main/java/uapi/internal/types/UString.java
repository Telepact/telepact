package uapi.internal.types;

import static uapi.internal.generation.GenerateRandomString.generateRandomString;
import static uapi.internal.validation.ValidateString.validateString;

import java.util.List;
import java.util.Map;

import uapi.RandomGenerator;
import uapi.internal.validation.ValidationFailure;

public class UString implements UType {
    public static final String _STRING_NAME = "String";

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, Map<String, Object> select, String fn,
            List<UTypeDeclaration> typeParameters) {
        return validateString(value);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<UTypeDeclaration> typeParameters,
            RandomGenerator randomGenerator) {
        return generateRandomString(blueprintValue, useBlueprintValue, randomGenerator);
    }

    @Override
    public String getName() {
        return _STRING_NAME;
    }
}