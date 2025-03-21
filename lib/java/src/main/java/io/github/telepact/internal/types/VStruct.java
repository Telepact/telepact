package io.github.telepact.internal.types;

import static io.github.telepact.internal.generation.GenerateRandomStruct.generateRandomStruct;
import static io.github.telepact.internal.validation.ValidateStruct.validateStruct;

import java.util.List;
import java.util.Map;

import io.github.telepact.internal.generation.GenerateContext;
import io.github.telepact.internal.validation.ValidateContext;
import io.github.telepact.internal.validation.ValidationFailure;

public class VStruct implements VType {

    public static final String _STRUCT_NAME = "Object";

    public final String name;
    public final Map<String, VFieldDeclaration> fields;

    public VStruct(String name, Map<String, VFieldDeclaration> fields) {
        this.name = name;
        this.fields = fields;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<VTypeDeclaration> typeParameters, ValidateContext ctx) {
        return validateStruct(value, this.name, this.fields, ctx);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            List<VTypeDeclaration> typeParameters, GenerateContext ctx) {
        return generateRandomStruct(blueprintValue, useBlueprintValue, this.fields, ctx);
    }

    @Override
    public String getName() {
        return _STRUCT_NAME;
    }
}
