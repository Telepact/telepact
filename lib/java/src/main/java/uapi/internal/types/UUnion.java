package uapi.internal.types;

import static uapi.internal.generation.GenerateRandomUnion.generateRandomUnion;
import static uapi.internal.validation.ValidateUnion.validateUnion;

import java.util.List;
import java.util.Map;

import uapi.internal.generation.GenerateContext;
import uapi.internal.validation.ValidateContext;
import uapi.internal.validation.ValidationFailure;

public class UUnion implements UType {

    public static final String _UNION_NAME = "Object";

    public final String name;
    public final Map<String, UStruct> tags;
    public final Map<String, Integer> tagIndices;

    public UUnion(String name, Map<String, UStruct> tags, Map<String, Integer> tagIndices) {
        this.name = name;
        this.tags = tags;
        this.tagIndices = tagIndices;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<UTypeDeclaration> typeParameters, ValidateContext ctx) {
        return validateUnion(value, this.name, this.tags, ctx);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            List<UTypeDeclaration> typeParameters, GenerateContext ctx) {
        return generateRandomUnion(blueprintValue, useBlueprintValue, this.tags, ctx);
    }

    @Override
    public String getName() {
        return _UNION_NAME;
    }
}
