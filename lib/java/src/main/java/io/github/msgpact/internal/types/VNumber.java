package io.github.msgpact.internal.types;

import static io.github.msgpact.internal.generation.GenerateRandomNumber.generateRandomNumber;
import static io.github.msgpact.internal.validation.ValidateNumber.validateNumber;

import java.util.List;

import io.github.msgpact.internal.generation.GenerateContext;
import io.github.msgpact.internal.validation.ValidateContext;
import io.github.msgpact.internal.validation.ValidationFailure;

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
