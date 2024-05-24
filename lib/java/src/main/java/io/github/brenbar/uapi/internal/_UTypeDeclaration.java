package io.github.brenbar.uapi.internal;

import java.util.List;
import java.util.Map;

import io.github.brenbar.uapi._RandomGenerator;

import static io.github.brenbar.uapi.internal.ValidateValueOfType.validateValueOfType;
import static io.github.brenbar.uapi.internal.GenerateRandomValueOfType.generateRandomValueOfType;

public class _UTypeDeclaration {
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

    public List<_ValidationFailure> validate(Object value, Map<String, Object> select, String fn,
            List<_UTypeDeclaration> generics) {
        return validateValueOfType(value, select, fn, generics, this.type, this.nullable, this.typeParameters);
    }

    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<_UTypeDeclaration> generics,
            _RandomGenerator randomGenerator) {
        return generateRandomValueOfType(blueprintValue, useBlueprintValue,
                includeOptionalFields, randomizeOptionalFields,
                generics, randomGenerator, this.type, this.nullable, this.typeParameters);
    }
}
