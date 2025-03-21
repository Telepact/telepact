package io.github.telepact.internal.types;

import static io.github.telepact.internal.generation.GenerateRandomInteger.generateRandomInteger;
import static io.github.telepact.internal.validation.ValidateInteger.validateInteger;

import java.util.List;

import io.github.telepact.internal.generation.GenerateContext;
import io.github.telepact.internal.validation.ValidateContext;
import io.github.telepact.internal.validation.ValidationFailure;

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
