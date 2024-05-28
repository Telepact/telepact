package uapi.internal.types;

import static uapi.internal.generation.GenerateRandomAny.generateRandomAny;

import java.util.List;
import java.util.Map;

import uapi.RandomGenerator;
import uapi.internal.validation.ValidationFailure;

public class UAny implements UType {

    static final String _ANY_NAME = "Any";

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, Map<String, Object> select, String fn,
            List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics) {
        return List.of();
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics,
            RandomGenerator randomGenerator) {
        return generateRandomAny(randomGenerator);
    }

    @Override
    public String getName(List<UTypeDeclaration> generics) {
        return _ANY_NAME;
    }
}
