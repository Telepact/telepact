package io.github.brenbar.uapi;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

class _UFn implements _UType {

    public final String name;
    public final _UUnion call;
    public final _UUnion result;
    public final String extendsRegex;

    public _UFn(String name, _UUnion call, _UUnion output, String extendsRegex) {
        this.name = name;
        this.call = call;
        this.result = output;
        this.extendsRegex = extendsRegex;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return this.call.validate(value, typeParameters, generics);
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics, RandomGenerator random) {
        final Map<String, _UStruct> callCases = this.call.cases;
        if (useStartingValue) {
            final var startingFnValue = (Map<String, Object>) startingValue;
            return _UUnion.constructRandomUnion(callCases, startingFnValue, includeRandomOptionalFields,
                    List.of(), random);
        } else {
            return _UUnion.constructRandomUnion(callCases, new HashMap<>(), includeRandomOptionalFields,
                    List.of(), random);
        }
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        return "Object";
    }
}
