package io.github.brenbar.uapi.internal;

import java.util.List;
import java.util.Map;

import io.github.brenbar.uapi.RandomGenerator;

import static io.github.brenbar.uapi.internal.ValidateValueOfType.validateValueOfType;
import static io.github.brenbar.uapi.internal.GenerateRandomValueOfType.generateRandomValueOfType;

public class UTypeDeclaration {
    public final UType type;
    public final boolean nullable;
    public final List<UTypeDeclaration> typeParameters;

    public UTypeDeclaration(
            UType type,
            boolean nullable, List<UTypeDeclaration> typeParameters) {
        this.type = type;
        this.nullable = nullable;
        this.typeParameters = typeParameters;
    }

    public List<ValidationFailure> validate(Object value, Map<String, Object> select, String fn,
            List<UTypeDeclaration> generics) {
        return validateValueOfType(value, select, fn, generics, this.type, this.nullable, this.typeParameters);
    }

    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<UTypeDeclaration> generics,
            RandomGenerator randomGenerator) {
        return generateRandomValueOfType(blueprintValue, useBlueprintValue,
                includeOptionalFields, randomizeOptionalFields,
                generics, randomGenerator, this.type, this.nullable, this.typeParameters);
    }
}
