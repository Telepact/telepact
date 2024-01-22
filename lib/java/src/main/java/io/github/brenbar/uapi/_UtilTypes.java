package io.github.brenbar.uapi;

import java.util.List;
import java.util.Map;

interface _UType {

    public int getTypeParameterCount();

    public List<_ValidationFailure> validate(Object value, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics);

    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator randomGenerator);

    public String getName(List<_UTypeDeclaration> generics);
}

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

    public List<_ValidationFailure> validate(Object value, List<_UTypeDeclaration> generics) {
        return _Util.validateValueOfType(value, generics, this.type, this.nullable, this.typeParameters);
    }

    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> generics,
            _RandomGenerator randomGenerator) {
        return _Util.generateRandomValueOfType(startingValue, useStartingValue,
                includeRandomOptionalFields,
                generics, randomGenerator, this.type, this.nullable, this.typeParameters);
    }
}

class _ValidationFailure {
    public final List<Object> path;
    public final String reason;
    public final Map<String, Object> data;

    public _ValidationFailure(List<Object> path, String reason, Map<String, Object> data) {
        this.path = path;
        this.reason = reason;
        this.data = data;
    }
}
