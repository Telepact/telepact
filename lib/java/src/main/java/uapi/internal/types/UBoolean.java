package uapi.internal.types;

import static uapi.internal.generation.GenerateRandomBoolean.generateRandomBoolean;
import static uapi.internal.validation.ValidateBoolean.validateBoolean;

import java.util.List;

import uapi.internal.generation.GenerateContext;
import uapi.internal.validation.ValidateContext;
import uapi.internal.validation.ValidationFailure;

public class UBoolean implements UType {

    public static final String _BOOLEAN_NAME = "Boolean";

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<UTypeDeclaration> typeParameters, ValidateContext ctx) {
        return validateBoolean(value);
    }

    @Override
    public Object generateRandomValue(GenerateContext ctx) {
        return generateRandomBoolean(ctx);
    }

    @Override
    public String getName() {
        return _BOOLEAN_NAME;
    }

}
