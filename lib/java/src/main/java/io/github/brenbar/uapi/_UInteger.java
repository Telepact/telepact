package io.github.brenbar.uapi;

import java.util.List;

class _UInteger implements _UType {
    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<_Util._ValidationFailure> validate(Object value, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return _Util._integerValidate(value);
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics, _RandomGenerator randomGenerator) {
        return _Util._integerGenerateRandomValue(startingValue, useStartingValue, randomGenerator);
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        return _Util._INTEGER_NAME;
    }
}
