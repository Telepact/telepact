package io.github.telepact.internal.types;

import static io.github.telepact.internal.generation.GenerateRandomArray.generateRandomArray;
import static io.github.telepact.internal.validation.ValidateArray.validateArray;

import java.util.List;

import io.github.telepact.internal.generation.GenerateContext;
import io.github.telepact.internal.validation.ValidateContext;
import io.github.telepact.internal.validation.ValidationFailure;

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
