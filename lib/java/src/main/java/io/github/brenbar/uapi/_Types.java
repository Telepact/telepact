package io.github.brenbar.uapi;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

class UTrait {
    public final String name;
    public final _UUnion errors;

    public UTrait(String name, _UUnion errors) {
        this.name = name;
        this.errors = errors;
    }
}

class BinaryEncoding {

    public final Map<String, Integer> encodeMap;
    public final Map<Integer, String> decodeMap;
    public final Integer checksum;

    public BinaryEncoding(Map<String, Integer> binaryEncoding, Integer checksum) {
        this.encodeMap = binaryEncoding;
        this.decodeMap = binaryEncoding.entrySet().stream()
                .collect(Collectors.toMap(e -> e.getValue(), e -> e.getKey()));
        this.checksum = checksum;
    }
}

interface BinaryEncoder {
    List<Object> encode(List<Object> message) throws BinaryEncoderUnavailableError;

    List<Object> decode(List<Object> message) throws BinaryEncoderUnavailableError;
}

class ValidationFailure {
    public final List<Object> path;
    public final String reason;
    public final Map<String, Object> data;

    public ValidationFailure(List<Object> path, String reason, Map<String, Object> data) {
        this.path = path;
        this.reason = reason;
        this.data = data;
    }
}

class SchemaParseFailure {
    public final List<Object> path;
    public final String reason;
    public final Map<String, Object> data;

    public SchemaParseFailure(List<Object> path, String reason, Map<String, Object> data) {
        this.path = path;
        this.reason = reason;
        this.data = data;
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
