package io.github.msgpact.internal.types;

import static io.github.msgpact.internal.generation.GenerateRandomArray.generateRandomArray;
import static io.github.msgpact.internal.validation.ValidateArray.validateArray;

import java.util.List;

import io.github.msgpact.internal.generation.GenerateContext;
import io.github.msgpact.internal.validation.ValidateContext;
import io.github.msgpact.internal.validation.ValidationFailure;

public class VArray implements VType {

    public static final String _ARRAY_NAME = "Array";

    @Override
    public int getTypeParameterCount() {
        return 1;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<VTypeDeclaration> typeParameters, ValidateContext ctx) {
        return validateArray(value, typeParameters, ctx);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            List<VTypeDeclaration> typeParameters, GenerateContext ctx) {
        return generateRandomArray(blueprintValue, useBlueprintValue, typeParameters, ctx);
    }

    @Override
    public String getName() {
        return _ARRAY_NAME;
    }
}
