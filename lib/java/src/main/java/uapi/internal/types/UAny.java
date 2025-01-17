package uapi.internal.types;

import static uapi.internal.generation.GenerateRandomAny.generateRandomAny;

import java.util.List;

import uapi.internal.generation.GenerateContext;
import uapi.internal.validation.ValidateContext;
import uapi.internal.validation.ValidationFailure;

public class UAny implements UType {

    static final String _ANY_NAME = "Any";

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(
            Object value, List<UTypeDeclaration> typeParameters, ValidateContext ctx) {
        return List.of();
    }

    @Override
    public Object generateRandomValue(GenerateContext ctx) {
        return generateRandomAny(ctx);
    }

    @Override
    public String getName() {
        return _ANY_NAME;
    }
}
