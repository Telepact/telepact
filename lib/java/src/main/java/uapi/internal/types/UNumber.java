package uapi.internal.types;

import static uapi.internal.generation.GenerateRandomNumber.generateRandomNumber;
import static uapi.internal.validation.ValidateNumber.validateNumber;

import java.util.List;
import java.util.Map;

import uapi.internal.generation.GenerateContext;
import uapi.internal.validation.ValidationFailure;

public class UNumber implements UType {
    public static final String _NUMBER_NAME = "Number";

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, Map<String, Object> select, String fn,
            List<UTypeDeclaration> typeParameters) {
        return validateNumber(value);
    }

    @Override
    public Object generateRandomValue(GenerateContext ctx) {
        return generateRandomNumber(ctx);
    }

    @Override
    public String getName() {
        return _NUMBER_NAME;
    }
}
