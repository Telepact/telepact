package io.github.brenbar.uapi;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

class _UMockCall implements _UType {

    public final Map<String, _UType> types;

    public _UMockCall(Map<String, _UType> types) {
        this.types = types;
    }

    @Override
    public List<_ValidationFailure> validate(Object givenObj, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        final Map<String, Object> givenMap;
        try {
            givenMap = _CastUtil.asMap(givenObj);
        } catch (ClassCastException e) {
            return _ValidateUtil.getTypeUnexpectedValidationFailure(new ArrayList<Object>(), givenObj, "Object");
        }

        final var regexString = "^fn\\..*$";

        final var matches = givenMap.keySet().stream().filter(k -> k.matches(regexString)).toList();
        if (matches.size() != 1) {
            return List.of(new _ValidationFailure(new ArrayList<Object>(), "ObjectKeyRegexMatchCountUnexpected",
                    Map.of("regex", regexString, "actual", matches.size(), "expected", 1)));
        }

        final var functionName = matches.get(0);
        final var functionDef = (_UFn) this.types.get(functionName);
        final var input = givenMap.get(functionName);

        final _UUnion functionDefCall = functionDef.call;
        final String functionDefName = functionDef.name;
        final Map<String, _UStruct> functionDefCallCases = functionDefCall.cases;

        final var inputFailures = functionDefCallCases.get(functionDefName).validate(input, List.of(), List.of());

        final var inputFailuresWithPath = new ArrayList<_ValidationFailure>();
        for (var f : inputFailures) {
            List<Object> newPath = _ValidateUtil.prepend(functionName, f.path);

            inputFailuresWithPath.add(new _ValidationFailure(newPath, f.reason, f.data));
        }

        return inputFailuresWithPath.stream()
                .filter(f -> !f.reason.equals("RequiredStructFieldMissing")).toList();
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator randomGenerator) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'generateRandomValue'");
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        return "_ext._Call";
    }

}
