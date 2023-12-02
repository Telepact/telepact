package io.github.brenbar.japi;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

class JApiSchemaTuple {
    public final List<Object> original;
    public final Map<String, Type> parsed;

    public JApiSchemaTuple(List<Object> original, Map<String, Type> parsed) {
        this.original = original;
        this.parsed = parsed;
    }
}

class FieldNameAndFieldDeclaration {

    public final String fieldName;
    public final FieldDeclaration fieldDeclaration;

    public FieldNameAndFieldDeclaration(
            String fieldName,
            FieldDeclaration fieldDeclaration) {
        this.fieldName = fieldName;
        this.fieldDeclaration = fieldDeclaration;
    }
}

class FieldDeclaration {

    public final TypeDeclaration typeDeclaration;
    public final boolean optional;

    public FieldDeclaration(
            TypeDeclaration typeDeclaration,
            boolean optional) {
        this.typeDeclaration = typeDeclaration;
        this.optional = optional;
    }
}

class TypeDeclaration {
    public final Type type;
    public final boolean nullable;
    public final List<TypeDeclaration> typeParameters;

    public TypeDeclaration(
            Type type,
            boolean nullable, List<TypeDeclaration> typeParameters) {
        this.type = type;
        this.nullable = nullable;
        this.typeParameters = typeParameters;
    }
}

class TypeDeclarationRoot {
    public final Type type;
    public final boolean nullable;

    public TypeDeclarationRoot(
            Type type,
            boolean nullable) {
        this.type = type;
        this.nullable = nullable;
    }
}

interface Type {
    public int getTypeParameterCount();
}

class JsonBoolean implements Type {

    @Override
    public int getTypeParameterCount() {
        return 0;
    }
}

class JsonInteger implements Type {
    @Override
    public int getTypeParameterCount() {
        return 0;
    }
}

class JsonNumber implements Type {
    @Override
    public int getTypeParameterCount() {
        return 0;
    }
}

class JsonString implements Type {
    @Override
    public int getTypeParameterCount() {
        return 0;
    }
}

class JsonArray implements Type {

    @Override
    public int getTypeParameterCount() {
        return 1;
    }
}

class JsonObject implements Type {

    @Override
    public int getTypeParameterCount() {
        return 1;
    }
}

class JsonAny implements Type {
    @Override
    public int getTypeParameterCount() {
        return 0;
    }
}

class Generic implements Type {
    public final int index;

    public Generic(int index) {
        this.index = index;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }
}

class Struct implements Type {

    public final String name;
    public final Map<String, FieldDeclaration> fields;
    public final int typeParameterCount;

    public Struct(String name, Map<String, FieldDeclaration> fields, int typeParameterCount) {
        this.name = name;
        this.fields = fields;
        this.typeParameterCount = typeParameterCount;
    }

    @Override
    public int getTypeParameterCount() {
        return this.typeParameterCount;
    }
}

class Enum implements Type {

    public final String name;
    public final Map<String, Struct> values;
    public final int typeParameterCount;

    public Enum(String name, Map<String, Struct> values, int typeParameterCount) {
        this.name = name;
        this.values = values;
        this.typeParameterCount = typeParameterCount;
    }

    @Override
    public int getTypeParameterCount() {
        return this.typeParameterCount;
    }
}

class Fn implements Type {

    public final String name;
    public final Struct arg;
    public final Enum result;

    public Fn(String name, Struct input, Enum output) {
        this.name = name;
        this.arg = input;
        this.result = output;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }
}

class Trait implements Type {
    public final String name;
    public final Fn fn;
    public final String regex;

    public Trait(String name, Fn fn, String regex) {
        this.name = name;
        this.fn = fn;
        this.regex = regex;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }
}

class Info implements Type {
    public final String name;

    public Info(String name) {
        this.name = name;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }
}

class Ext implements Type {
    public final String name;
    public final TypeExtension typeExtension;
    public final int typeParameterCount;

    public Ext(String name, TypeExtension typeExtension, int typeParameterCount) {
        this.name = name;
        this.typeExtension = typeExtension;
        this.typeParameterCount = typeParameterCount;
    }

    @Override
    public int getTypeParameterCount() {
        return this.typeParameterCount;
    }
}

class BinaryEncoding {

    public final Map<String, Long> encodeMap;
    public final Map<Long, String> decodeMap;
    public final Integer checksum;

    public BinaryEncoding(Map<String, Long> binaryEncoding, Integer checksum) {
        this.encodeMap = binaryEncoding;
        this.decodeMap = binaryEncoding.entrySet().stream()
                .collect(Collectors.toMap(e -> Long.valueOf(e.getValue()), e -> e.getKey()));
        this.checksum = checksum;
    }
}

interface BinaryEncoder {
    List<Object> encode(List<Object> message) throws BinaryEncoderUnavailableError;

    List<Object> decode(List<Object> message) throws BinaryEncoderUnavailableError;
}

class ValidationFailure {
    public final String path;
    public final String reason;

    public ValidationFailure(String path, String reason) {
        this.path = path;
        this.reason = reason;
    }
}

class Invocation {
    final String functionName;
    final Map<String, Object> functionArgument;
    boolean verified = false;

    public Invocation(String functionName, Map<String, Object> functionArgument) {
        this.functionName = functionName;
        this.functionArgument = functionArgument;
    }
}
