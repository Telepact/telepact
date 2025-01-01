package uapi.internal.types;

import static uapi.internal.generation.GenerateRandomInteger.generateRandomInteger;
import static uapi.internal.validation.ValidateInteger.validateInteger;

import java.util.List;
import java.util.Map;

import uapi.RandomGenerator;
import uapi.internal.validation.ValidationFailure;

public class UInteger implements UType {
    public static final String _INTEGER_NAME = "Integer";

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, Map<String, Object> select, String fn,
            List<UTypeDeclaration> typeParameters) {
        return validateInteger(value);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<UTypeDeclaration> typeParameters,
            RandomGenerator randomGenerator) {
        return generateRandomInteger(blueprintValue, useBlueprintValue, randomGenerator);
    }

    @Override
    public String getName() {
        return _INTEGER_NAME;
    }
}
