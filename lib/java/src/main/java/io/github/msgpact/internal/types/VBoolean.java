package io.github.msgpact.internal.types;

import static io.github.msgpact.internal.generation.GenerateRandomBoolean.generateRandomBoolean;
import static io.github.msgpact.internal.validation.ValidateBoolean.validateBoolean;

import java.util.List;

import io.github.msgpact.internal.generation.GenerateContext;
import io.github.msgpact.internal.validation.ValidateContext;
import io.github.msgpact.internal.validation.ValidationFailure;

public class VBoolean implements VType {

    public static final String _BOOLEAN_NAME = "Boolean";

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<VTypeDeclaration> typeParameters, ValidateContext ctx) {
        return validateBoolean(value);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            List<VTypeDeclaration> typeParameters, GenerateContext ctx) {
        return generateRandomBoolean(blueprintValue, useBlueprintValue, ctx);
    }

    @Override
    public String getName() {
        return _BOOLEAN_NAME;
    }

}
