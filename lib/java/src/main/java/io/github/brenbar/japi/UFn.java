package io.github.brenbar.japi;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class UFn implements UType {

    public final String name;
    public final UUnion call;
    public final UUnion result;

    public UFn(String name, UUnion call, UUnion output) {
        this.name = name;
        this.call = call;
        this.result = output;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics) {
        return this.call.validate(value, typeParameters, generics);
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics,
            RandomGenerator random) {
        if (useStartingValue) {
            var startingFnValue = (Map<String, Object>) startingValue;
            return UUnion.constructRandomUnion(this.call.cases, startingFnValue, includeRandomOptionalFields,
                    List.of(),
                    random);
        } else {
            return UUnion.constructRandomUnion(this.call.cases, new HashMap<>(), includeRandomOptionalFields,
                    List.of(),
                    random);
        }
    }

    @Override
    public String getName(List<UTypeDeclaration> generics) {
        return "Object";
    }
}
