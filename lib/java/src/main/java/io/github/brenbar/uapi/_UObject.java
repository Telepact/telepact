package io.github.brenbar.uapi;

import java.util.List;

class _UObject implements _UType {

    @Override
    public int getTypeParameterCount() {
        return 1;
    }

    @Override
    public List<_Util._ValidationFailure> validate(Object value, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return _Util._objectValidate(value, typeParameters, generics);
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics, _RandomGenerator randomGenerator) {
        return _Util._objectGenerateRandomValue(startingValue, useStartingValue, includeRandomOptionalFields,
                typeParameters, generics, randomGenerator);
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        return _Util._OBJECT_NAME;
    }

}
