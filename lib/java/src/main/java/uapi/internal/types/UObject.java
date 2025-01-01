package uapi.internal.types;

import static uapi.internal.generation.GenerateRandomObject.generateRandomObject;
import static uapi.internal.validation.ValidateObject.validateObject;

import java.util.List;
import java.util.Map;

import uapi.RandomGenerator;
import uapi.internal.validation.ValidationFailure;

public class UObject implements UType {

    public static final String _OBJECT_NAME = "Object";

    @Override
    public int getTypeParameterCount() {
        return 1;
    }

    @Override
    public List<ValidationFailure> validate(Object value, Map<String, Object> select, String fn,
            List<UTypeDeclaration> typeParameters) {
        return validateObject(value, select, fn, typeParameters);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<UTypeDeclaration> typeParameters,
            RandomGenerator randomGenerator) {
        return generateRandomObject(blueprintValue, useBlueprintValue, includeOptionalFields,
                randomizeOptionalFields,
                typeParameters, randomGenerator);
    }

    @Override
    public String getName() {
        return _OBJECT_NAME;
    }

}
