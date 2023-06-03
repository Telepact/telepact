package io.github.brenbar.japi;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.msgpack.jackson.dataformat.MessagePackFactory;

import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.stream.Collectors;

public interface Serializer {

    public static class SerializationError extends RuntimeException {
        public SerializationError(Throwable cause) {
            super(cause);
        }
    }
    public static class DeserializationError extends Exception {
        public DeserializationError(Throwable cause) {
            super(cause);
        }
    }
    public static class BinaryEncodingError extends RuntimeException {
        public BinaryEncodingError(Throwable cause) {
            super(cause);
        }
    }
    public static class BinaryDecodingError extends Exception {
        public BinaryDecodingError(Throwable cause) {
            super(cause);
        }
    }


    byte[] serializeToJson(List<Object> japiMessage);
    byte[] serializeToBinary(List<Object> japiMessage, Map<String, Integer> binaryEncoding);
    List<Object> deserializeFromJson(byte[] bytes) throws DeserializationError;
    List<Object> deserializeFromBinary(byte[] bytes, Map<Integer, String> binaryEncodingReverse, Long binaryHash) throws BinaryDecodingError, DeserializationError;

    public static class Default implements Serializer {

        private ObjectMapper jsonMapper = new ObjectMapper();
        private ObjectMapper binaryMapper = new ObjectMapper(new MessagePackFactory());

        @Override
        public byte[] serializeToJson(List<Object> japiMessage) {
            try {
                return jsonMapper.writeValueAsBytes(japiMessage);
            } catch (JsonProcessingException e) {
                throw new SerializationError(e);
            }
        }

        @Override
        public byte[] serializeToBinary(List<Object> japiMessage, Map<String, Integer> binaryEncoding) {
            try {
                var encodedMessageType = encode(japiMessage.get(0), binaryEncoding);
                var headers = japiMessage.get(1);
                var encodedBody = encode(japiMessage.get(2), binaryEncoding);
                try {
                    return binaryMapper.writeValueAsBytes(List.of(encodedMessageType, headers, encodedBody));
                } catch (JsonProcessingException e) {
                    throw new SerializationError(e);
                }
            } catch (Exception e) {
                throw new BinaryEncodingError(e);
            }
        }

        @Override
        public List<Object> deserializeFromJson(byte[] bytes) throws DeserializationError {
            try {
                return jsonMapper.readValue(bytes, new TypeReference<List<Object>>() {});
            } catch (IOException e) {
                throw new DeserializationError(e);
            }
        }

        @Override
        public List<Object> deserializeFromBinary(byte[] bytes, Map<Integer, String> binaryEncodingReversed, Long binaryHash) throws BinaryDecodingError, DeserializationError {
            try {
                var encodedJapiMessage = binaryMapper.readValue(bytes, new TypeReference<List<Object>>() {});
                try {
                    var decodedMessageType = decode(encodedJapiMessage.get(0), binaryEncodingReversed);
                    var headers = (Map<String, Object>) encodedJapiMessage.get(1);
                    var givenHash = (Long) headers.get("_bin");
                    if (Objects.equals(givenHash, binaryHash)) {
                        throw new Exception("Client provided binary hash does not match server");
                    }
                    var decodedBody = decode(encodedJapiMessage.get(2), binaryEncodingReversed);
                    return List.of(decodedMessageType, headers, decodedBody);
                } catch (Exception e) {
                    throw new BinaryDecodingError(e);
                }
            } catch (IOException e) {
                throw new DeserializationError(e);
            }
        }

        private Object decode(Object given, Map<Integer, String> binaryEncodingReversed) {
            if (given instanceof Map<?,?> m) {
                return m.entrySet().stream().collect(Collectors.toMap(e -> binaryEncodingReversed.get(e.getKey()), e -> decode(e.getValue(), binaryEncodingReversed)));
            } else if (given instanceof List<?> l) {
                return l.stream().map(e -> decode(e, binaryEncodingReversed));
            } else {
                return given;
            }
        }

        private Object encode(Object given, Map<String, Integer> binaryEncoding) {
            if (given instanceof Map<?,?> m) {
                return m.entrySet().stream().collect(Collectors.toMap(e -> binaryEncoding.get(e.getKey()), e -> encode(e.getValue(), binaryEncoding)));
            } else if (given instanceof List<?> l) {
                return l.stream().map(e -> encode(e, binaryEncoding));
            } else {
                return given;
            }
        }
    }
}
