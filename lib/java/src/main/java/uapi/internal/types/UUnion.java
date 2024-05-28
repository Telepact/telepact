package uapi.internal.types;

import static uapi.internal.generation.GenerateRandomUnion.generateRandomUnion;
import static uapi.internal.validation.ValidateUnion.validateUnion;

import java.util.List;
import java.util.Map;

import uapi.RandomGenerator;
import uapi.internal.validation.ValidationFailure;

public class UUnion implements UType {

    public static final String _UNION_NAME = "Object";

    public final String name;
    public final Map<String, UStruct> cases;
    public final Map<String, Integer> caseIndices;
    public final int typeParameterCount;

    public UUnion(String name, Map<String, UStruct> cases, Map<String, Integer> caseIndices, int typeParameterCount) {
        this.name = name;
        this.cases = cases;
        this.caseIndices = caseIndices;
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
        return validateUnion(value, select, fn, typeParameters, generics, this.name, this.cases);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics,
            RandomGenerator random) {
        return generateRandomUnion(blueprintValue, useBlueprintValue, includeOptionalFields,
                randomizeOptionalFields,
                typeParameters, generics, random, this.cases);
    }

    @Override
    public String getName(List<UTypeDeclaration> generics) {
        return _UNION_NAME;
    }
}
