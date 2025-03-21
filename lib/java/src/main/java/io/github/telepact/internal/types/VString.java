package io.github.telepact.internal.types;

import static io.github.telepact.internal.generation.GenerateRandomString.generateRandomString;
import static io.github.telepact.internal.validation.ValidateString.validateString;

import java.util.List;

import io.github.telepact.internal.generation.GenerateContext;
import io.github.telepact.internal.validation.ValidateContext;
import io.github.telepact.internal.validation.ValidationFailure;

public class VString implements VType {
    public static final String _STRING_NAME = "String";

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<VTypeDeclaration> typeParameters, ValidateContext ctx) {
        return validateString(value);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            List<VTypeDeclaration> typeParameters, GenerateContext ctx) {
        return generateRandomString(blueprintValue, useBlueprintValue, ctx);
    }

    @Override
    public String getName() {
        return _STRING_NAME;
    }
}