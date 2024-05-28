package uapi.internal.types;

import static uapi.internal.validation.ValidateMockStub.validateMockStub;

import java.util.List;
import java.util.Map;

import uapi.RandomGenerator;
import uapi.internal.validation.ValidationFailure;

public class UMockStub implements UType {

    static final String _MOCK_STUB_NAME = "_ext.Stub_";

    public final Map<String, UType> types;

    public UMockStub(Map<String, UType> types) {
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
        return validateMockStub(givenObj, select, fn, typeParameters, generics, this.types);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics, RandomGenerator randomGenerator) {
        throw new UnsupportedOperationException("Not implemented");
    }

    @Override
    public String getName(List<UTypeDeclaration> generics) {
        return _MOCK_STUB_NAME;
    }

}
