package uapi.internal.types;

import static uapi.internal.validation.ValidateSelect.validateSelect;

import java.util.List;
import java.util.Map;

import uapi.RandomGenerator;
import uapi.internal.validation.ValidationFailure;

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
            List<UTypeDeclaration> typeParameters) {
        return validateSelect(givenObj, select, fn, typeParameters, this.types);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<UTypeDeclaration> typeParameters,
            RandomGenerator randomGenerator) {
        throw new UnsupportedOperationException("Not implemented");
    }

    @Override
    public String getName() {
        return _SELECT;
    }

}
