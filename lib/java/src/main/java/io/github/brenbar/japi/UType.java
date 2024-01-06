package io.github.brenbar.japi;

import java.util.List;

interface UType {
    public int getTypeParameterCount();

    public List<ValidationFailure> validate(Object value, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics);

    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics,
            RandomGenerator random);

    public String getName(List<UTypeDeclaration> generics);
}