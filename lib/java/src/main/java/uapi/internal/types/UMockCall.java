package uapi.internal.types;

import static uapi.internal.validation.ValidateMockCall.validateMockCall;
import static uapi.internal.generation.GenerateRandomUMockCall.generateRandomUMockCall;

import java.util.List;
import java.util.Map;

import uapi.internal.generation.GenerateContext;
import uapi.internal.validation.ValidateContext;
import uapi.internal.validation.ValidationFailure;

public class UMockCall implements UType {

    public static final String _MOCK_CALL_NAME = "_ext.Call_";

    public final Map<String, UType> types;

    public UMockCall(Map<String, UType> types) {
        this.types = types;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object givenObj,
            List<UTypeDeclaration> typeParameters, ValidateContext ctx) {
        return validateMockCall(givenObj, typeParameters, this.types, ctx);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            List<UTypeDeclaration> typeParameters, GenerateContext ctx) {
        return generateRandomUMockCall(this.types, ctx);
    }

    @Override
    public String getName() {
        return _MOCK_CALL_NAME;
    }

}
