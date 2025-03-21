package io.github.telepact.internal.types;

import static io.github.telepact.internal.generation.GenerateRandomUnion.generateRandomUnion;
import static io.github.telepact.internal.validation.ValidateUnion.validateUnion;

import java.util.List;
import java.util.Map;

import io.github.telepact.internal.generation.GenerateContext;
import io.github.telepact.internal.validation.ValidateContext;
import io.github.telepact.internal.validation.ValidationFailure;

public class VUnion implements VType {

    public static final String _UNION_NAME = "Object";

    public final String name;
    public final Map<String, VStruct> tags;
    public final Map<String, Integer> tagIndices;

    public VUnion(String name, Map<String, VStruct> tags, Map<String, Integer> tagIndices) {
        this.name = name;
        this.tags = tags;
        this.tagIndices = tagIndices;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<VTypeDeclaration> typeParameters, ValidateContext ctx) {
        return validateUnion(value, this.name, this.tags, ctx);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            List<VTypeDeclaration> typeParameters, GenerateContext ctx) {
        return generateRandomUnion(blueprintValue, useBlueprintValue, this.tags, ctx);
    }

    @Override
    public String getName() {
        return _UNION_NAME;
    }
}
