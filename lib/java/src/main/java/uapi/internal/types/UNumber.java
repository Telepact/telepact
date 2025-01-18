package uapi.internal.types;

import static uapi.internal.generation.GenerateRandomNumber.generateRandomNumber;
import static uapi.internal.validation.ValidateNumber.validateNumber;

import java.util.List;

import uapi.internal.generation.GenerateContext;
import uapi.internal.validation.ValidateContext;
import uapi.internal.validation.ValidationFailure;

public class UNumber implements UType {
    public static final String _NUMBER_NAME = "Number";

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<UTypeDeclaration> typeParameters, ValidateContext ctx) {
        return validateNumber(value);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            List<UTypeDeclaration> typeParameters, GenerateContext ctx) {
        return generateRandomNumber(blueprintValue, useBlueprintValue, ctx);
    }

    @Override
    public String getName() {
        return _NUMBER_NAME;
    }
}
