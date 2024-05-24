package io.github.brenbar.uapi.internal;

import java.util.List;
import java.util.Map;

import io.github.brenbar.uapi._RandomGenerator;

import static io.github.brenbar.uapi.internal.GenerateRandomAny.generateRandomAny;

public class _UAny implements _UType {

    static final String _ANY_NAME = "Any";

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<_ValidationFailure> validate(Object value, Map<String, Object> select, String fn,
            List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return List.of();
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator randomGenerator) {
        return generateRandomAny(randomGenerator);
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        return _ANY_NAME;
    }
}
