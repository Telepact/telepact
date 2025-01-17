package uapi.internal.types;

import static uapi.internal.generation.GenerateRandomArray.generateRandomArray;
import static uapi.internal.validation.ValidateArray.validateArray;

import java.util.List;

import uapi.internal.generation.GenerateContext;
import uapi.internal.validation.ValidateContext;
import uapi.internal.validation.ValidationFailure;

public class UArray implements UType {

    public static final String _ARRAY_NAME = "Array";

    @Override
    public int getTypeParameterCount() {
        return 1;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<UTypeDeclaration> typeParameters, ValidateContext ctx) {
        return validateArray(value, typeParameters, ctx);
    }

    @Override
    public Object generateRandomValue(GenerateContext ctx) {
        return generateRandomArray(ctx);
    }

    @Override
    public String getName() {
        return _ARRAY_NAME;
    }
}
