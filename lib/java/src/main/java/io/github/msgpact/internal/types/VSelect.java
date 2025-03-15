package io.github.msgpact.internal.types;

import static io.github.msgpact.internal.generation.GenerateRandomSelect.generateRandomSelect;
import static io.github.msgpact.internal.validation.ValidateSelect.validateSelect;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import io.github.msgpact.internal.generation.GenerateContext;
import io.github.msgpact.internal.validation.ValidateContext;
import io.github.msgpact.internal.validation.ValidationFailure;

public class VSelect implements VType {

    public static final String _SELECT = "Object";

    public final Map<String, Object> possibleSelects = new HashMap<>();

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object givenObj,
            List<VTypeDeclaration> typeParameters, ValidateContext ctx) {
        return validateSelect(givenObj, this.possibleSelects, ctx);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            List<VTypeDeclaration> typeParameters, GenerateContext ctx) {
        return generateRandomSelect(this.possibleSelects, ctx);
    }

    @Override
    public String getName() {
        return _SELECT;
    }

}
