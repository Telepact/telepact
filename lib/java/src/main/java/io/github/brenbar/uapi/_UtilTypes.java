package io.github.brenbar.uapi;

import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

class _SchemaParseFailure {
    public final List<Object> path;
    public final String reason;
    public final Map<String, Object> data;
    public final String key;

    public _SchemaParseFailure(List<Object> path, String reason, Map<String, Object> data, String key) {
        this.path = path;
        this.reason = reason;
        this.data = data;
        this.key = key;
    }
}

interface _UType {

    public int getTypeParameterCount();

    public List<_ValidationFailure> validate(Object value, Map<String, Object> select, String fn,
            List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics);

    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<_UTypeDeclaration> typeParameters,
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

    public List<_ValidationFailure> validate(Object value, Map<String, Object> select, String fn,
            List<_UTypeDeclaration> generics) {
        return _Util.validateValueOfType(value, select, fn, generics, this.type, this.nullable, this.typeParameters);
    }

    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<_UTypeDeclaration> generics,
            _RandomGenerator randomGenerator) {
        return _Util.generateRandomValueOfType(blueprintValue, useBlueprintValue,
                includeOptionalFields, randomizeOptionalFields,
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
    public List<_ValidationFailure> validate(Object value, Map<String, Object> select, String fn,
            List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        final var typeDeclaration = generics.get(this.index);
        return typeDeclaration.validate(value, select, fn, List.of());
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator randomGenerator) {
        final var genericTypeDeclaration = generics.get(this.index);
        return genericTypeDeclaration.generateRandomValue(blueprintValue, useBlueprintValue,
                includeOptionalFields, randomizeOptionalFields, List.of(), randomGenerator);
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
    public List<_ValidationFailure> validate(Object value, Map<String, Object> select, String fn,
            List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return List.of();
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<_UTypeDeclaration> typeParameters,
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
    public List<_ValidationFailure> validate(Object value, Map<String, Object> select, String fn,
            List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return _Util.validateBoolean(value);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator randomGenerator) {
        return _Util.generateRandomBoolean(blueprintValue, useBlueprintValue, randomGenerator);
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
    public List<_ValidationFailure> validate(Object value, Map<String, Object> select, String fn,
            List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return _Util.validateInteger(value);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics, _RandomGenerator randomGenerator) {
        return _Util.generateRandomInteger(blueprintValue, useBlueprintValue, randomGenerator);
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
    public List<_ValidationFailure> validate(Object value, Map<String, Object> select, String fn,
            List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return _Util.validateNumber(value);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator randomGenerator) {
        return _Util.generateRandomNumber(blueprintValue, useBlueprintValue, randomGenerator);
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
    public List<_ValidationFailure> validate(Object value, Map<String, Object> select, String fn,
            List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return _Util.validateString(value);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator randomGenerator) {
        return _Util.generateRandomString(blueprintValue, useBlueprintValue, randomGenerator);
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
    public List<_ValidationFailure> validate(Object value, Map<String, Object> select, String fn,
            List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return _Util.validateArray(value, select, fn, typeParameters, generics);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator randomGenerator) {
        return _Util.generateRandomArray(blueprintValue, useBlueprintValue, includeOptionalFields,
                randomizeOptionalFields,
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
    public List<_ValidationFailure> validate(Object value, Map<String, Object> select, String fn,
            List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return _Util.validateObject(value, select, fn, typeParameters, generics);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics, _RandomGenerator randomGenerator) {
        return _Util.generateRandomObject(blueprintValue, useBlueprintValue, includeOptionalFields,
                randomizeOptionalFields,
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
    public List<_ValidationFailure> validate(Object value, Map<String, Object> select, String fn,
            List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return _Util.validateStruct(value, select, fn, typeParameters, generics, this.name, this.fields);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator random) {
        return _Util.generateRandomStruct(blueprintValue, useBlueprintValue, includeOptionalFields,
                randomizeOptionalFields,
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
    public List<_ValidationFailure> validate(Object value, Map<String, Object> select, String fn,
            List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return _Util.validateUnion(value, select, fn, typeParameters, generics, this.name, this.cases);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator random) {
        return _Util.generateRandomUnion(blueprintValue, useBlueprintValue, includeOptionalFields,
                randomizeOptionalFields,
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
    public List<_ValidationFailure> validate(Object value, Map<String, Object> select, String fn,
            List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return this.call.validate(value, select, fn, typeParameters, generics);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics, _RandomGenerator randomGenerator) {
        return _Util.generateRandomFn(blueprintValue, useBlueprintValue, includeOptionalFields, randomizeOptionalFields,
                typeParameters, generics, randomGenerator, this.call.cases);
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        return _Util._FN_NAME;
    }
}

class _USelect implements _UType {

    public final Map<String, _UType> types;

    public _USelect(Map<String, _UType> types) {
        this.types = types;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<_ValidationFailure> validate(Object givenObj, Map<String, Object> select, String fn,
            List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return _Util.validateSelect(givenObj, select, fn, typeParameters, generics, this.types);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator randomGenerator) {
        throw new UnsupportedOperationException("Not implemented");
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        return _Util._SELECT;
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
    public List<_ValidationFailure> validate(Object givenObj, Map<String, Object> select, String fn,
            List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return _Util.validateMockCall(givenObj, select, fn, typeParameters, generics, this.types);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator randomGenerator) {
        throw new UnsupportedOperationException("Not implemented");
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
    public List<_ValidationFailure> validate(Object givenObj, Map<String, Object> select, String fn,
            List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return _Util.validateMockStub(givenObj, select, fn, typeParameters, generics, this.types);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics, _RandomGenerator randomGenerator) {
        throw new UnsupportedOperationException("Not implemented");
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        return _Util._MOCK_STUB_NAME;
    }

}

class _UError {
    public final String name;
    public final _UUnion errors;

    public _UError(String name, _UUnion errors) {
        this.name = name;
        this.errors = errors;
    }
}

class _UHeaders {
    public final String name;
    public final Map<String, _UFieldDeclaration> requestHeaders;
    public final Map<String, _UFieldDeclaration> responseHeaders;

    public _UHeaders(
            final String name,
            final Map<String, _UFieldDeclaration> requestHeaders,
            final Map<String, _UFieldDeclaration> responseHeaders) {
        this.name = name;
        this.requestHeaders = requestHeaders;
        this.responseHeaders = responseHeaders;
    }
}

class _DeserializationError extends RuntimeException {

    public _DeserializationError(Throwable cause) {
        super(cause);
    }

    public _DeserializationError(String message) {
        super(message);
    }

}

class _BinaryEncoderUnavailableError extends RuntimeException {

}

class _BinaryEncodingMissing extends RuntimeException {

    public _BinaryEncodingMissing(Object key) {
        super("Missing binary encoding for %s".formatted(String.valueOf(key)));
    }

}

class _InvalidMessage extends RuntimeException {

    public _InvalidMessage() {
        super();
    }

    public _InvalidMessage(Throwable cause) {
        super(cause);
    }
}

class _InvalidMessageBody extends RuntimeException {

}

class _BinaryEncoding {

    public final Map<String, Integer> encodeMap;
    public final Map<Integer, String> decodeMap;
    public final Integer checksum;

    public _BinaryEncoding(Map<String, Integer> binaryEncodingMap, Integer checksum) {
        this.encodeMap = binaryEncodingMap;
        this.decodeMap = binaryEncodingMap.entrySet().stream()
                .collect(Collectors.toMap(e -> e.getValue(), e -> e.getKey()));
        this.checksum = checksum;
    }
}

interface _BinaryEncoder {
    List<Object> encode(List<Object> message);

    List<Object> decode(List<Object> message);
}

class _ServerBinaryEncoder implements _BinaryEncoder {

    private final _BinaryEncoding binaryEncoder;

    public _ServerBinaryEncoder(_BinaryEncoding binaryEncoder) {
        this.binaryEncoder = binaryEncoder;
    }

    @Override
    public List<Object> encode(List<Object> message) {
        return _Util.serverBinaryEncode(message, binaryEncoder);
    }

    @Override
    public List<Object> decode(List<Object> message) {
        return _Util.serverBinaryDecode(message, binaryEncoder);
    }

}

class _ClientBinaryEncoder implements _BinaryEncoder {

    private final Map<Integer, _BinaryEncoding> recentBinaryEncoders;
    private final ClientBinaryStrategy binaryChecksumStrategy;

    public _ClientBinaryEncoder(ClientBinaryStrategy binaryChecksumStrategy) {
        this.recentBinaryEncoders = new ConcurrentHashMap<>();
        this.binaryChecksumStrategy = binaryChecksumStrategy;
    }

    @Override
    public List<Object> encode(List<Object> message) throws _BinaryEncoderUnavailableError {
        return _Util.clientBinaryEncode(message, this.recentBinaryEncoders,
                this.binaryChecksumStrategy);
    }

    @Override
    public List<Object> decode(List<Object> message) throws _BinaryEncoderUnavailableError {
        return _Util.clientBinaryDecode(message, this.recentBinaryEncoders, this.binaryChecksumStrategy);
    }

}

class _MockStub {
    final String whenFunction;
    final Map<String, Object> whenArgument;
    final Map<String, Object> thenResult;
    final boolean allowArgumentPartialMatch;
    int count;

    public _MockStub(String whenFunction, Map<String, Object> whenArgument,
            Map<String, Object> thenResult, boolean allowArgumentPartialMatch, int count) {
        this.whenFunction = whenFunction;
        this.whenArgument = whenArgument;
        this.thenResult = thenResult;
        this.allowArgumentPartialMatch = allowArgumentPartialMatch;
        this.count = count;
    }
}

class _MockInvocation {
    public final String functionName;
    public final Map<String, Object> functionArgument;
    public boolean verified = false;

    public _MockInvocation(String functionName, Map<String, Object> functionArgument) {
        this.functionName = functionName;
        this.functionArgument = functionArgument;
    }
}