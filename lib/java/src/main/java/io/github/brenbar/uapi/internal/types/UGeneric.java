package io.github.brenbar.uapi.internal.types;

import java.util.List;
import java.util.Map;

import io.github.brenbar.uapi.RandomGenerator;
import io.github.brenbar.uapi.internal.validation.ValidationFailure;

public class UGeneric implements UType {
    public final int index;

    public UGeneric(int index) {
        this.index = index;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, Map<String, Object> select, String fn,
            List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics) {
        final var typeDeclaration = generics.get(this.index);
        return typeDeclaration.validate(value, select, fn, List.of());
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics,
            RandomGenerator randomGenerator) {
        final var genericTypeDeclaration = generics.get(this.index);
        return genericTypeDeclaration.generateRandomValue(blueprintValue, useBlueprintValue,
                includeOptionalFields, randomizeOptionalFields, List.of(), randomGenerator);
    }

    @Override
    public String getName(List<UTypeDeclaration> generics) {
        final var typeDeclaration = generics.get(this.index);
        return typeDeclaration.type.getName(generics);
    }
}
