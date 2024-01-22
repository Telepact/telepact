package io.github.brenbar.uapi;

import java.util.List;

class _UGeneric implements _UType {
    public final int index;

    public _UGeneric(int index) {
        this.index = index;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<_ValidationFailure> validate(Object value, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        final var typeDeclaration = generics.get(this.index);
        return typeDeclaration.validate(value, List.of());
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator randomGenerator) {
        final var genericTypeDeclaration = generics.get(this.index);
        return genericTypeDeclaration.generateRandomValue(startingValue, useStartingValue,
                includeRandomOptionalFields, List.of(), randomGenerator);
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        final var typeDeclaration = generics.get(this.index);
        return typeDeclaration.type.getName(generics);
    }
}
