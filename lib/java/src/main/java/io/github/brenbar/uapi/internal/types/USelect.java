package io.github.brenbar.uapi.internal.types;

import java.util.List;
import java.util.Map;

import io.github.brenbar.uapi.RandomGenerator;
import io.github.brenbar.uapi.internal.ValidationFailure;

import static io.github.brenbar.uapi.internal.ValidateSelect.validateSelect;

public class USelect implements UType {

    public static final String _SELECT = "Object";

    public final Map<String, UType> types;

    public USelect(Map<String, UType> types) {
        this.types = types;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object givenObj, Map<String, Object> select, String fn,
            List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics) {
        return validateSelect(givenObj, select, fn, typeParameters, generics, this.types);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics,
            RandomGenerator randomGenerator) {
        throw new UnsupportedOperationException("Not implemented");
    }

    @Override
    public String getName(List<UTypeDeclaration> generics) {
        return _SELECT;
    }

}
