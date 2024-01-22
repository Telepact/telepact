package io.github.brenbar.uapi;

import java.util.List;
import java.util.Map;

class _UUnion implements _UType {

    public final String name;
    public final Map<String, _UStruct> cases;
    public final int typeParameterCount;

    public _UUnion(String name, Map<String, _UStruct> cases, int typeParameterCount) {
        this.name = name;
        this.cases = cases;
        this.typeParameterCount = typeParameterCount;
    }

    @Override
    public int getTypeParameterCount() {
        return this.typeParameterCount;
    }

    @Override
    public List<_ValidationFailure> validate(Object value, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return _Util.validateUnion(value, typeParameters, generics, this.cases);
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator random) {
        return _Util.generateRandomUnion(startingValue, useStartingValue, includeRandomOptionalFields,
                typeParameters, generics, random, this.cases);
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        return _Util._UNION_NAME;
    }
}
