package uapi.internal.types;

import static uapi.internal.generation.GenerateRandomInteger.generateRandomInteger;
import static uapi.internal.validation.ValidateInteger.validateInteger;

import java.util.List;

import uapi.internal.generation.GenerateContext;
import uapi.internal.validation.ValidateContext;
import uapi.internal.validation.ValidationFailure;

public class UInteger implements UType {
    public static final String _INTEGER_NAME = "Integer";

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<UTypeDeclaration> typeParameters, ValidateContext ctx) {
        return validateInteger(value);
    }

    @Override
    public Object generateRandomValue(GenerateContext ctx) {
        return generateRandomInteger(ctx);
    }

    @Override
    public String getName() {
        return _INTEGER_NAME;
    }
}
