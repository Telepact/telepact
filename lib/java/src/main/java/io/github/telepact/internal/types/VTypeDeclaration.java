package io.github.telepact.internal.types;

import static io.github.telepact.internal.generation.GenerateRandomValueOfType.generateRandomValueOfType;
import static io.github.telepact.internal.validation.ValidateValueOfType.validateValueOfType;

import java.util.List;
import java.util.Map;

import io.github.telepact.internal.generation.GenerateContext;
import io.github.telepact.internal.validation.ValidateContext;
import io.github.telepact.internal.validation.ValidationFailure;

public class VTypeDeclaration {
    public final VType type;
    public final boolean nullable;
    public final List<VTypeDeclaration> typeParameters;

    public VTypeDeclaration(
            VType type,
            boolean nullable, List<VTypeDeclaration> typeParameters) {
        this.type = type;
        this.nullable = nullable;
        this.typeParameters = typeParameters;
    }

    public List<ValidationFailure> validate(Object value, ValidateContext ctx) {
        return validateValueOfType(value, this.type, this.nullable, this.typeParameters, ctx);
    }

    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            GenerateContext ctx) {
        return generateRandomValueOfType(blueprintValue, useBlueprintValue, this.type, this.nullable,
                this.typeParameters, ctx);
    }
}
