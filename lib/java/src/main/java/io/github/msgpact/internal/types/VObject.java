package io.github.msgpact.internal.types;

import static io.github.msgpact.internal.generation.GenerateRandomObject.generateRandomObject;
import static io.github.msgpact.internal.validation.ValidateObject.validateObject;

import java.util.List;

import io.github.msgpact.internal.generation.GenerateContext;
import io.github.msgpact.internal.validation.ValidateContext;
import io.github.msgpact.internal.validation.ValidationFailure;

public class VObject implements VType {

    public static final String _OBJECT_NAME = "Object";

    @Override
    public int getTypeParameterCount() {
        return 1;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<VTypeDeclaration> typeParameters, ValidateContext ctx) {
        return validateObject(value, typeParameters, ctx);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            List<VTypeDeclaration> typeParameters, GenerateContext ctx) {
        return generateRandomObject(blueprintValue, useBlueprintValue, typeParameters, ctx);
    }

    @Override
    public String getName() {
        return _OBJECT_NAME;
    }

}
