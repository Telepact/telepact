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
    public final int typeParameterCount;

    public UStruct(String name, Map<String, UFieldDeclaration> fields, int typeParameterCount) {
        this.name = name;
        this.fields = fields;
        this.typeParameterCount = typeParameterCount;
    }

    @Override
    public int getTypeParameterCount() {
        return this.typeParameterCount;
    }

    @Override
    public List<ValidationFailure> validate(Object value, Map<String, Object> select, String fn,
            List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics) {
        return validateStruct(value, select, fn, typeParameters, generics, this.name, this.fields);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics,
            RandomGenerator random) {
        return generateRandomStruct(blueprintValue, useBlueprintValue, includeOptionalFields,
                randomizeOptionalFields,
                typeParameters, generics, random, this.fields);
    }

    @Override
    public String getName(List<UTypeDeclaration> generics) {
        return _STRUCT_NAME;
    }
}
