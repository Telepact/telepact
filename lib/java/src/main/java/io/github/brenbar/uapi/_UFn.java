package io.github.brenbar.uapi;

import java.util.List;

class _UFn implements _UType {

    public final String name;
    public final _UUnion call;
    public final _UUnion result;
    public final String errorsRegex;

    public _UFn(String name, _UUnion call, _UUnion output, String errorsRegex) {
        this.name = name;
        this.call = call;
        this.result = output;
        this.errorsRegex = errorsRegex;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<_ValidationFailure> validate(Object value, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return this.call.validate(value, typeParameters, generics);
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics, _RandomGenerator randomGenerator) {
        return _Util.fnGenerateRandomValue(startingValue, useStartingValue, includeRandomOptionalFields,
                typeParameters, generics, randomGenerator, this.call.cases);
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        return _Util._FN_NAME;
    }
}
