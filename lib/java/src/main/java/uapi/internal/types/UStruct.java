package uapi.internal.types;

import static uapi.internal.generation.GenerateRandomStruct.generateRandomStruct;
import static uapi.internal.validation.ValidateStruct.validateStruct;

import java.util.List;
import java.util.Map;

import uapi.RandomGenerator;
import uapi.internal.validation.ValidationFailure;

public class UStruct implements UType {

    public static final String _STRUCT_NAME = "Object";

    public final String name;
    public final Map<String, UFieldDeclaration> fields;

    public UStruct(String name, Map<String, UFieldDeclaration> fields) {
        this.name = name;
        this.fields = fields;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, Map<String, Object> select, String fn,
            List<UTypeDeclaration> typeParameters) {
        return validateStruct(value, select, fn, this.name, this.fields);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<UTypeDeclaration> typeParameters,
            RandomGenerator random) {
        return generateRandomStruct(blueprintValue, useBlueprintValue, includeOptionalFields,
                randomizeOptionalFields,
                random, this.fields);
    }

    @Override
    public String getName() {
        return _STRUCT_NAME;
    }
}
