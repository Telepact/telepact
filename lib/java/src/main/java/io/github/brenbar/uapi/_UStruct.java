package io.github.brenbar.uapi;

import java.util.List;
import java.util.Map;

class _UStruct implements _UType {

    public final String name;
    public final Map<String, _UFieldDeclaration> fields;
    public final int typeParameterCount;

    public _UStruct(String name, Map<String, _UFieldDeclaration> fields, int typeParameterCount) {
        this.name = name;
        this.fields = fields;
        this.typeParameterCount = typeParameterCount;
    }

    @Override
    public int getTypeParameterCount() {
        return this.typeParameterCount;
    }

    @Override
    public List<_ValidationFailure> validate(Object value, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return _Util._structValidate(value, typeParameters, generics, this.fields);
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator random) {
        return _Util._structGenerateRandomValue(startingValue, useStartingValue, includeRandomOptionalFields,
                typeParameters, generics, random, this.fields);
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        return _Util._STRUCT_NAME;
    }
}
