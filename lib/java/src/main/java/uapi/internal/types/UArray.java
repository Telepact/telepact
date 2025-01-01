package uapi.internal.types;

import static uapi.internal.generation.GenerateRandomArray.generateRandomArray;
import static uapi.internal.validation.ValidateArray.validateArray;

import java.util.List;
import java.util.Map;

import uapi.RandomGenerator;
import uapi.internal.validation.ValidationFailure;

public class UArray implements UType {

    public static final String _ARRAY_NAME = "Array";

    @Override
    public int getTypeParameterCount() {
        return 1;
    }

    @Override
    public List<ValidationFailure> validate(Object value, Map<String, Object> select, String fn,
            List<UTypeDeclaration> typeParameters) {
        return validateArray(value, select, fn, typeParameters);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<UTypeDeclaration> typeParameters,
            RandomGenerator randomGenerator) {
        return generateRandomArray(blueprintValue, useBlueprintValue, includeOptionalFields,
                randomizeOptionalFields,
                typeParameters, randomGenerator);
    }

    @Override
    public String getName() {
        return _ARRAY_NAME;
    }
}
