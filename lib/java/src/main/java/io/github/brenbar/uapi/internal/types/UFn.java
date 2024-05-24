package io.github.brenbar.uapi.internal.types;

import java.util.List;
import java.util.Map;

import io.github.brenbar.uapi.RandomGenerator;
import io.github.brenbar.uapi.internal.ValidationFailure;

import static io.github.brenbar.uapi.internal.GenerateRandomFn.generateRandomFn;

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
            List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics) {
        return this.call.validate(value, select, fn, typeParameters, generics);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics, RandomGenerator randomGenerator) {
        return generateRandomFn(blueprintValue, useBlueprintValue, includeOptionalFields, randomizeOptionalFields,
                typeParameters, generics, randomGenerator, this.call.cases);
    }

    @Override
    public String getName(List<UTypeDeclaration> generics) {
        return _FN_NAME;
    }
}
