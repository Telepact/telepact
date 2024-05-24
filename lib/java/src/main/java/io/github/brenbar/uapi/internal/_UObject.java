package io.github.brenbar.uapi.internal;

import java.util.List;
import java.util.Map;

import io.github.brenbar.uapi._RandomGenerator;

import static io.github.brenbar.uapi.internal.GenerateRandomObject.generateRandomObject;
import static io.github.brenbar.uapi.internal.ValidateObject.validateObject;

public class _UObject implements _UType {

    static final String _OBJECT_NAME = "Object";

    @Override
    public int getTypeParameterCount() {
        return 1;
    }

    @Override
    public List<_ValidationFailure> validate(Object value, Map<String, Object> select, String fn,
            List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return validateObject(value, select, fn, typeParameters, generics);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics, _RandomGenerator randomGenerator) {
        return generateRandomObject(blueprintValue, useBlueprintValue, includeOptionalFields,
                randomizeOptionalFields,
                typeParameters, generics, randomGenerator);
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        return _OBJECT_NAME;
    }

}
