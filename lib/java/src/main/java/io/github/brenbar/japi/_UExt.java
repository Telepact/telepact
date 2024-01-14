package io.github.brenbar.japi;

import java.util.List;

public class _UExt implements _UType {
    public final String name;
    public final _UType typeExtension;
    public final int typeParameterCount;

    public _UExt(String name, _UType typeExtension, int typeParameterCount) {
        this.name = name;
        this.typeExtension = typeExtension;
        this.typeParameterCount = typeParameterCount;
    }

    @Override
    public int getTypeParameterCount() {
        return this.typeParameterCount;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return this.typeExtension.validate(value, typeParameters, generics);
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters, List<_UTypeDeclaration> generics,
            RandomGenerator random) {
        return this.typeExtension.generateRandomValue(startingValue, useStartingValue, includeRandomOptionalFields,
                typeParameters, generics, random);
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        return this.name;
    }
}
