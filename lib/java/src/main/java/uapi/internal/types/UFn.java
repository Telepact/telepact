package uapi.internal.types;

import static uapi.internal.generation.GenerateRandomUnion.generateRandomUnion;

import java.util.List;
import java.util.Map;

import uapi.internal.generation.GenerateContext;
import uapi.internal.validation.ValidateContext;
import uapi.internal.validation.ValidationFailure;

public class UFn implements UType {

    static final String _FN_NAME = "Object";

    public final String name;
    public final UUnion call;
    public final UUnion result;
    public final String errorsRegex;

    public UFn(String name, UUnion call, UUnion output, String errorsRegex) {
        this.name = name;
        this.call = call;
        this.result = output;
        this.errorsRegex = errorsRegex;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<UTypeDeclaration> typeParameters, ValidateContext ctx) {
        return this.call.validate(value, typeParameters, ctx);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            List<UTypeDeclaration> typeParameters, GenerateContext ctx) {
        return generateRandomUnion(blueprintValue, useBlueprintValue, this.call.tags, ctx);
    }

    @Override
    public String getName() {
        return _FN_NAME;
    }
}
