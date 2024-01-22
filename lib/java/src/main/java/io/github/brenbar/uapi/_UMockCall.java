package io.github.brenbar.uapi;

import java.util.List;
import java.util.Map;

class _UMockCall implements _UType {

    public final Map<String, _UType> types;

    public _UMockCall(Map<String, _UType> types) {
        this.types = types;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<_ValidationFailure> validate(Object givenObj, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return _Util.mockCallValidate(givenObj, typeParameters, generics, this.types);
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator randomGenerator) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'generateRandomValue'");
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        return _Util._MOCK_CALL_NAME;
    }

}
