package uapi.internal.types;

import static uapi.internal.validation.ValidateSelect.validateSelect;
import static uapi.internal.generation.GenerateRandomSelect.generateRandomSelect;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import uapi.internal.generation.GenerateContext;
import uapi.internal.validation.ValidationFailure;

public class USelect implements UType {

    public static final String _SELECT = "Object";

    public final Map<String, Object> possibleSelects = new HashMap<>();

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object givenObj, Map<String, Object> select, String fn,
            List<UTypeDeclaration> typeParameters) {
        return validateSelect(givenObj, fn, this.possibleSelects);
    }

    @Override
    public Object generateRandomValue(GenerateContext ctx) {
        return generateRandomSelect(this.possibleSelects, ctx);
    }

    @Override
    public String getName() {
        return _SELECT;
    }

}
