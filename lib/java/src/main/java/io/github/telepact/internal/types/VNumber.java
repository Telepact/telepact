package io.github.telepact.internal.types;

import static io.github.telepact.internal.generation.GenerateRandomNumber.generateRandomNumber;
import static io.github.telepact.internal.validation.ValidateNumber.validateNumber;

import java.util.List;

import io.github.telepact.internal.generation.GenerateContext;
import io.github.telepact.internal.validation.ValidateContext;
import io.github.telepact.internal.validation.ValidationFailure;

public class VNumber implements VType {
    public static final String _NUMBER_NAME = "Number";

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<VTypeDeclaration> typeParameters, ValidateContext ctx) {
        return validateNumber(value);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            List<VTypeDeclaration> typeParameters, GenerateContext ctx) {
        return generateRandomNumber(blueprintValue, useBlueprintValue, ctx);
    }

    @Override
    public String getName() {
        return _NUMBER_NAME;
    }
}
