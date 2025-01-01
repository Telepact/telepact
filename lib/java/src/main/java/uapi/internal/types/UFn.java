package uapi.internal.types;

import static uapi.internal.generation.GenerateRandomFn.generateRandomFn;

import java.util.List;
import java.util.Map;

import uapi.RandomGenerator;
import uapi.internal.validation.ValidationFailure;

public class UFn implements UType {

    static final String _FN_NAME = "Object";

    public final String name;
    public final UUnion call;
    public final UUnion result;
    public final String errorsRegex;

    public UFn(String name, UUnion call, UUnion output, String errorsRegex) {
        this.name = name;
        this.call = call;
        this.result = output;
        this.errorsRegex = errorsRegex;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, Map<String, Object> select, String fn,
            List<UTypeDeclaration> typeParameters) {
        return this.call.validate(value, select, fn, typeParameters);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<UTypeDeclaration> typeParameters,
            RandomGenerator randomGenerator) {
        return generateRandomFn(blueprintValue, useBlueprintValue, includeOptionalFields, randomizeOptionalFields,
                typeParameters, randomGenerator, this.call.cases);
    }

    @Override
    public String getName() {
        return _FN_NAME;
    }
}
