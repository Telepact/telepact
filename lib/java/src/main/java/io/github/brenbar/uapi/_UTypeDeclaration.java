package io.github.brenbar.uapi;

import java.util.List;

class _UTypeDeclaration {
    public final _UType type;
    public final boolean nullable;
    public final List<_UTypeDeclaration> typeParameters;

    public _UTypeDeclaration(
            _UType type,
            boolean nullable, List<_UTypeDeclaration> typeParameters) {
        this.type = type;
        this.nullable = nullable;
        this.typeParameters = typeParameters;
    }

    public List<_Util._ValidationFailure> validate(Object value, List<_UTypeDeclaration> generics) {
        return _Util._typeDeclarationValidate(value, generics, this.type, this.nullable, this.typeParameters);
    }

    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> generics,
            _RandomGenerator randomGenerator) {
        return _Util._typeDeclarationGenerateRandomValue(startingValue, useStartingValue, includeRandomOptionalFields,
                generics, randomGenerator, this.type, this.nullable, this.typeParameters);
    }
}
