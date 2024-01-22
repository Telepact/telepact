package io.github.brenbar.uapi;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;

interface _UType {

    public int getTypeParameterCount();

    public List<_ValidationFailure> validate(Object value, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics);

    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator randomGenerator);

    public String getName(List<_UTypeDeclaration> generics);
}

class _UTypeDeclaration {
    public final _UType type;
    public final boolean nullable;
    public final List<_UTypeDeclaration> typeParameters;

    public _UTypeDeclaration(
            _UType type,
            boolean nullable, List<_UTypeDeclaration> typeParameters) {
        this.type = type;
        this.nullable = nullable;
        this.typeParameters = typeParameters;
    }

    public List<_ValidationFailure> validate(Object value, List<_UTypeDeclaration> generics) {
        return _Util.validateValueOfType(value, generics, this.type, this.nullable, this.typeParameters);
    }

    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> generics,
            _RandomGenerator randomGenerator) {
        return _Util.generateRandomValueOfType(startingValue, useStartingValue,
                includeRandomOptionalFields,
                generics, randomGenerator, this.type, this.nullable, this.typeParameters);
    }
}

class _UFieldDeclaration {
    public final String fieldName;
    public final _UTypeDeclaration typeDeclaration;
    public final boolean optional;

    public _UFieldDeclaration(
            String fieldName,
            _UTypeDeclaration typeDeclaration,
            boolean optional) {
        this.fieldName = fieldName;
        this.typeDeclaration = typeDeclaration;
        this.optional = optional;
    }
}

class _ValidationFailure {
    public final List<Object> path;
    public final String reason;
    public final Map<String, Object> data;

    public _ValidationFailure(List<Object> path, String reason, Map<String, Object> data) {
        this.path = path;
        this.reason = reason;
        this.data = data;
    }
}

class _UGeneric implements _UType {
    public final int index;

    public _UGeneric(int index) {
        this.index = index;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<_ValidationFailure> validate(Object value, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        final var typeDeclaration = generics.get(this.index);
        return typeDeclaration.validate(value, List.of());
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator randomGenerator) {
        final var genericTypeDeclaration = generics.get(this.index);
        return genericTypeDeclaration.generateRandomValue(startingValue, useStartingValue,
                includeRandomOptionalFields, List.of(), randomGenerator);
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        final var typeDeclaration = generics.get(this.index);
        return typeDeclaration.type.getName(generics);
    }
}

class _UAny implements _UType {

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<_ValidationFailure> validate(Object value, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return List.of();
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator randomGenerator) {
        return _Util.generateRandomAny(randomGenerator);
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        return _Util._ANY_NAME;
    }
}

class _UBoolean implements _UType {

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<_ValidationFailure> validate(Object value, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return _Util.validateBoolean(value);
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator randomGenerator) {
        return _Util.generateRandomBoolean(startingValue, useStartingValue, randomGenerator);
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        return _Util._BOOLEAN_NAME;
    }

}

class _UInteger implements _UType {
    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<_ValidationFailure> validate(Object value, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return _Util.validateInteger(value);
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics, _RandomGenerator randomGenerator) {
        return _Util.generateRandomInteger(startingValue, useStartingValue, randomGenerator);
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        return _Util._INTEGER_NAME;
    }
}

class _UNumber implements _UType {
    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<_ValidationFailure> validate(Object value, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return _Util.validateNumber(value);
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator randomGenerator) {
        return _Util.generateRandomNumber(startingValue, useStartingValue, randomGenerator);
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        return "Number";
    }
}

class _UString implements _UType {
    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<_ValidationFailure> validate(Object value, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return _Util.validateString(value);
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator randomGenerator) {
        return _Util.generateRandomString(startingValue, useStartingValue, randomGenerator);
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        return _Util._STRING_NAME;
    }
}

class _UArray implements _UType {

    @Override
    public int getTypeParameterCount() {
        return 1;
    }

    @Override
    public List<_ValidationFailure> validate(Object value, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return _Util.validateArray(value, typeParameters, generics);
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator randomGenerator) {
        return _Util.generateRandomArray(startingValue, useStartingValue, includeRandomOptionalFields,
                typeParameters, generics, randomGenerator);
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        return _Util._ARRAY_NAME;
    }
}

class _UObject implements _UType {

    @Override
    public int getTypeParameterCount() {
        return 1;
    }

    @Override
    public List<_ValidationFailure> validate(Object value, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return _Util.validateObject(value, typeParameters, generics);
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics, _RandomGenerator randomGenerator) {
        return _Util.generateRandomObject(startingValue, useStartingValue, includeRandomOptionalFields,
                typeParameters, generics, randomGenerator);
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        return _Util._OBJECT_NAME;
    }

}

class _UStruct implements _UType {

    public final String name;
    public final Map<String, _UFieldDeclaration> fields;
    public final int typeParameterCount;

    public _UStruct(String name, Map<String, _UFieldDeclaration> fields, int typeParameterCount) {
        this.name = name;
        this.fields = fields;
        this.typeParameterCount = typeParameterCount;
    }

    @Override
    public int getTypeParameterCount() {
        return this.typeParameterCount;
    }

    @Override
    public List<_ValidationFailure> validate(Object value, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return _Util.validateStruct(value, typeParameters, generics, this.fields);
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator random) {
        return _Util.generateRandomStruct(startingValue, useStartingValue, includeRandomOptionalFields,
                typeParameters, generics, random, this.fields);
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        return _Util._STRUCT_NAME;
    }
}

class _UUnion implements _UType {

    public final String name;
    public final Map<String, _UStruct> cases;
    public final int typeParameterCount;

    public _UUnion(String name, Map<String, _UStruct> cases, int typeParameterCount) {
        this.name = name;
        this.cases = cases;
        this.typeParameterCount = typeParameterCount;
    }

    @Override
    public int getTypeParameterCount() {
        return this.typeParameterCount;
    }

    @Override
    public List<_ValidationFailure> validate(Object value, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return _Util.validateUnion(value, typeParameters, generics, this.cases);
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator random) {
        return _Util.generateRandomUnion(startingValue, useStartingValue, includeRandomOptionalFields,
                typeParameters, generics, random, this.cases);
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        return _Util._UNION_NAME;
    }
}

class _UFn implements _UType {

    public final String name;
    public final _UUnion call;
    public final _UUnion result;
    public final String errorsRegex;

    public _UFn(String name, _UUnion call, _UUnion output, String errorsRegex) {
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
    public List<_ValidationFailure> validate(Object value, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return this.call.validate(value, typeParameters, generics);
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics, _RandomGenerator randomGenerator) {
        return _Util.generateRandomFn(startingValue, useStartingValue, includeRandomOptionalFields,
                typeParameters, generics, randomGenerator, this.call.cases);
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        return _Util._FN_NAME;
    }
}

class _UMockCall implements _UType {

    public final Map<String, _UType> types;

    public _UMockCall(Map<String, _UType> types) {
        this.types = types;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<_ValidationFailure> validate(Object givenObj, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return _Util.validateMockCall(givenObj, typeParameters, generics, this.types);
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
        return _Util._MOCK_CALL_NAME;
    }

}

class _UMockStub implements _UType {

    public final Map<String, _UType> types;

    public _UMockStub(Map<String, _UType> types) {
        this.types = types;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<_ValidationFailure> validate(Object givenObj, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        final var validationFailures = new ArrayList<_ValidationFailure>();

        final Map<String, Object> givenMap;
        try {
            givenMap = _CastUtil.asMap(givenObj);
        } catch (ClassCastException e) {
            return _Util.getTypeUnexpectedValidationFailure(List.of(), givenObj, "Object");
        }

        final var regexString = "^fn\\..*$";

        final var matches = givenMap.keySet().stream().filter(k -> k.matches(regexString)).toList();
        if (matches.size() != 1) {
            return List.of(
                    new _ValidationFailure(List.of(),
                            "ObjectKeyRegexMatchCountUnexpected",
                            Map.of("regex", regexString, "actual",
                                    matches.size(), "expected", 1)));

        }

        final var functionName = matches.get(0);
        final var functionDef = (_UFn) this.types.get(functionName);
        final var input = givenMap.get(functionName);

        final _UUnion functionDefCall = functionDef.call;
        final String functionDefName = functionDef.name;
        final Map<String, _UStruct> functionDefCallCases = functionDefCall.cases;
        final var inputFailures = functionDefCallCases.get(functionDefName).validate(input, List.of(), List.of());

        final var inputFailuresWithPath = new ArrayList<_ValidationFailure>();
        for (final var f : inputFailures) {
            final List<Object> thisPath = _ValidateUtil.prepend(functionName, f.path);

            inputFailuresWithPath.add(new _ValidationFailure(thisPath, f.reason, f.data));
        }

        final var inputFailuresWithoutMissingRequired = inputFailuresWithPath.stream()
                .filter(f -> !Objects.equals(f.reason, "RequiredStructFieldMissing")).toList();

        validationFailures.addAll(inputFailuresWithoutMissingRequired);

        final var resultDefKey = "->";

        if (!givenMap.containsKey(resultDefKey)) {
            return List.of(new _ValidationFailure(List.of(resultDefKey),
                    "RequiredObjectKeyMissing",
                    Map.of()));
        }

        final var output = givenMap.get(resultDefKey);
        final var outputFailures = functionDef.result.validate(output, List.of(), List.of());

        final var outputFailuresWithPath = new ArrayList<_ValidationFailure>();
        for (final var f : outputFailures) {
            final List<Object> thisPath = _ValidateUtil.prepend(resultDefKey, f.path);

            outputFailuresWithPath.add(new _ValidationFailure(thisPath, f.reason, f.data));
        }

        final var failuresWithoutMissingRequired = outputFailuresWithPath
                .stream()
                .filter(f -> !Objects.equals(f.reason, "RequiredStructFieldMissing"))
                .toList();

        validationFailures.addAll(failuresWithoutMissingRequired);

        return validationFailures;
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics, _RandomGenerator randomGenerator) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'generateRandomValue'");
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        return _Util._MOCK_STUB_NAME;
    }

}
