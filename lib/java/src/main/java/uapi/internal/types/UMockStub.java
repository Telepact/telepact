package uapi.internal.types;

import static uapi.internal.validation.ValidateMockStub.validateMockStub;
import static uapi.internal.generation.GenerateRandomUMockStub.generateRandomUMockStub;

import java.util.List;
import java.util.Map;

import uapi.internal.generation.GenerateContext;
import uapi.internal.validation.ValidateContext;
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
    public List<ValidationFailure> validate(Object givenObj,
            List<UTypeDeclaration> typeParameters, ValidateContext ctx) {
        return validateMockStub(givenObj, typeParameters, this.types, ctx);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            List<UTypeDeclaration> typeParameters, GenerateContext ctx) {
        return generateRandomUMockStub(this.types, ctx);
    }

    @Override
    public String getName() {
        return _MOCK_STUB_NAME;
    }

}
