package uapi.internal.types;

import static uapi.internal.generation.GenerateRandomAny.generateRandomAny;

import java.util.List;
import java.util.Map;

import uapi.internal.generation.GenerateContext;
import uapi.internal.validation.ValidationFailure;

public class UAny implements UType {

    static final String _ANY_NAME = "Any";

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, Map<String, Object> select, String fn,
            List<UTypeDeclaration> typeParameters) {
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
