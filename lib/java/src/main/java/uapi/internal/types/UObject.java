package uapi.internal.types;

import static uapi.internal.generation.GenerateRandomObject.generateRandomObject;
import static uapi.internal.validation.ValidateObject.validateObject;

import java.util.List;

import uapi.internal.generation.GenerateContext;
import uapi.internal.validation.ValidateContext;
import uapi.internal.validation.ValidationFailure;

public class UObject implements UType {

    public static final String _OBJECT_NAME = "Object";

    @Override
    public int getTypeParameterCount() {
        return 1;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<UTypeDeclaration> typeParameters, ValidateContext ctx) {
        return validateObject(value, typeParameters, ctx);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            List<UTypeDeclaration> typeParameters, GenerateContext ctx) {
        return generateRandomObject(blueprintValue, useBlueprintValue, typeParameters, ctx);
    }

    @Override
    public String getName() {
        return _OBJECT_NAME;
    }

}
