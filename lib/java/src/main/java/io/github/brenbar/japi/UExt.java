package io.github.brenbar.japi;

import java.util.List;

public class UExt implements UType {
    public final String name;
    public final TypeExtension typeExtension;
    public final int typeParameterCount;

    public UExt(String name, TypeExtension typeExtension, int typeParameterCount) {
        this.name = name;
        this.typeExtension = typeExtension;
        this.typeParameterCount = typeParameterCount;
    }

    @Override
    public int getTypeParameterCount() {
        return this.typeParameterCount;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics) {
        return this.typeExtension.validate(value);
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<UTypeDeclaration> typeParameters, List<UTypeDeclaration> generics,
            RandomGenerator random) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'generateRandomValue'");
    }

    @Override
    public String getName(List<UTypeDeclaration> generics) {
        return "Any";
    }
}
