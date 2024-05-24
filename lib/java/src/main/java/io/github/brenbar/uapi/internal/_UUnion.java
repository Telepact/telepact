package io.github.brenbar.uapi.internal;

import java.util.List;
import java.util.Map;

import io.github.brenbar.uapi._RandomGenerator;

import static io.github.brenbar.uapi.internal.GenerateRandomUnion.generateRandomUnion;
import static io.github.brenbar.uapi.internal.ValidateUnion.validateUnion;

public class _UUnion implements _UType {

    static final String _UNION_NAME = "Object";

    public final String name;
    public final Map<String, _UStruct> cases;
    public final Map<String, Integer> caseIndices;
    public final int typeParameterCount;

    public _UUnion(String name, Map<String, _UStruct> cases, Map<String, Integer> caseIndices, int typeParameterCount) {
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
    public List<_ValidationFailure> validate(Object value, Map<String, Object> select, String fn,
            List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return validateUnion(value, select, fn, typeParameters, generics, this.name, this.cases);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator random) {
        return generateRandomUnion(blueprintValue, useBlueprintValue, includeOptionalFields,
                randomizeOptionalFields,
                typeParameters, generics, random, this.cases);
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        return _UNION_NAME;
    }
}
