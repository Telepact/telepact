package io.github.msgpact.internal.types;

import static io.github.msgpact.internal.generation.GenerateRandomInteger.generateRandomInteger;
import static io.github.msgpact.internal.validation.ValidateInteger.validateInteger;

import java.util.List;

import io.github.msgpact.internal.generation.GenerateContext;
import io.github.msgpact.internal.validation.ValidateContext;
import io.github.msgpact.internal.validation.ValidationFailure;

public class VInteger implements VType {
    public static final String _INTEGER_NAME = "Integer";

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<VTypeDeclaration> typeParameters, ValidateContext ctx) {
        return validateInteger(value);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            List<VTypeDeclaration> typeParameters, GenerateContext ctx) {
        return generateRandomInteger(blueprintValue, useBlueprintValue, ctx);
    }

    @Override
    public String getName() {
        return _INTEGER_NAME;
    }
}
