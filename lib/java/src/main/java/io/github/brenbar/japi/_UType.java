package io.github.brenbar.japi;

import java.util.List;

public interface _UType {
        public int getTypeParameterCount();

        public List<ValidationFailure> validate(Object value, List<_UTypeDeclaration> typeParameters,
                        List<_UTypeDeclaration> generics);

        public Object generateRandomValue(Object startingValue, boolean useStartingValue,
                        boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
                        List<_UTypeDeclaration> generics,
                        RandomGenerator random);

        public String getName(List<_UTypeDeclaration> generics);
}