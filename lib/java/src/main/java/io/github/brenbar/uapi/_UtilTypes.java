package io.github.brenbar.uapi;

import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.Base64;
import java.util.List;
import java.util.Map;
import java.util.Objects;

class _RandomGenerator {
    private int seed = 0;
    private int collectionLengthMin;
    private int collectionLengthMax;

    public _RandomGenerator(int collectionLengthMin, int collectionLengthMax) {
        this.collectionLengthMin = collectionLengthMin;
        this.collectionLengthMax = collectionLengthMax;
    }

    public void setSeed(int seed) {
        this.seed = seed;
    }

    public int nextInt() {
        this.seed = (this.seed * 1_103_515_245 + 12_345) & 0x7fffffff;
        return seed;
    }

    public int nextInt(int ceiling) {
        if (ceiling == 0) {
            return 0;
        }
        return (int) nextInt() % ceiling;
    }

    public boolean nextBoolean() {
        return nextInt(31) > 15;
    }

    public String nextString() {
        var bytes = ByteBuffer.allocate(Integer.BYTES);
        bytes.putInt(nextInt());
        return Base64.getEncoder().withoutPadding().encodeToString(bytes.array());
    }

    public double nextDouble() {
        var x = (double) (nextInt(Integer.MAX_VALUE / 2) + (Integer.MAX_VALUE / 4));
        var y = Integer.MAX_VALUE;
        return x / (x + y);
    }

    public int nextCollectionLength() {
        return nextInt(this.collectionLengthMax - this.collectionLengthMin) + this.collectionLengthMin;
    }
}

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
        return _Util.validateMockStub(givenObj, typeParameters, generics, this.types);
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

class _UError {
    public final String name;
    public final _UUnion errors;

    public _UError(String name, _UUnion errors) {
        this.name = name;
        this.errors = errors;
    }
}

class _ServerBinaryEncoder implements _BinaryEncoder {

    private final _BinaryEncoding binaryEncoder;

    public _ServerBinaryEncoder(_BinaryEncoding binaryEncoder) {
        this.binaryEncoder = binaryEncoder;
    }

    @Override
    public List<Object> encode(List<Object> message) {
        return _BinaryEncodeUtil.serverBinaryEncode(message, binaryEncoder);
    }

    @Override
    public List<Object> decode(List<Object> message) throws BinaryEncoderUnavailableError {
        return _BinaryEncodeUtil.serverBinaryDecode(message, binaryEncoder);
    }

}
