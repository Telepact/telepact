package io.github.telepact.internal.types;

import static io.github.telepact.internal.generation.GenerateRandomUnion.generateRandomUnion;

import java.util.List;
import java.util.Map;

import io.github.telepact.internal.generation.GenerateContext;
import io.github.telepact.internal.validation.ValidateContext;
import io.github.telepact.internal.validation.ValidationFailure;

public class VFn implements VType {

    static final String _FN_NAME = "Object";

    public final String name;
    public final VUnion call;
    public final VUnion result;
    public final String errorsRegex;

    public VFn(String name, VUnion call, VUnion output, String errorsRegex) {
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
    public List<ValidationFailure> validate(Object value, List<VTypeDeclaration> typeParameters, ValidateContext ctx) {
        return this.call.validate(value, typeParameters, ctx);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            List<VTypeDeclaration> typeParameters, GenerateContext ctx) {
        return generateRandomUnion(blueprintValue, useBlueprintValue, this.call.tags, ctx);
    }

    @Override
    public String getName() {
        return _FN_NAME;
    }
}
