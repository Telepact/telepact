package io.github.brenbar.japi;

import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Deque;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.NoSuchElementException;
import java.util.Objects;
import java.util.Optional;
import java.util.TreeSet;
import java.util.stream.Collectors;

class InternalSerializer {

    static BinaryEncoder constructBinaryEncoder(JApiSchema jApiSchema) {
        var allKeys = new TreeSet<String>();
        for (var entry : jApiSchema.parsed.entrySet()) {
            allKeys.add(entry.getKey());
            if (entry.getValue() instanceof FunctionDefinition f) {
                allKeys.addAll(f.inputStruct.fields.keySet());
                allKeys.addAll(f.outputStruct.fields.keySet());
                for (var errorEnumEntry : f.errorEnum.values.entrySet()) {
                    allKeys.add(errorEnumEntry.getKey());
                    allKeys.addAll(errorEnumEntry.getValue().fields.keySet());
                }
            } else if (entry.getValue() instanceof TypeDefinition t) {
                var type = t.type;
                if (type instanceof Struct o) {
                    allKeys.addAll(o.fields.keySet());
                } else if (type instanceof Enum u) {
                    allKeys.addAll(u.values.keySet());
                }
            } else if (entry.getValue() instanceof ErrorDefinition e) {
                allKeys.addAll(e.fields.keySet());
            }
        }
        var i = (long) 0;
        var binaryEncoding = new HashMap<String, Long>();
        for (var key : allKeys) {
            binaryEncoding.put(key, i++);
        }
        var finalString = String.join("\n", allKeys);
        long binaryHash;
        try {
            var hash = MessageDigest.getInstance("SHA-256").digest(finalString.getBytes(StandardCharsets.UTF_8));
            var buffer = ByteBuffer.wrap(hash);
            binaryHash = buffer.getLong();
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        }
        return new BinaryEncoder(binaryEncoding, binaryHash);
    }

    static byte[] serialize(List<Object> message, BinaryEncodingStrategy binaryEncodingStrategy,
            SerializationStrategy serializationStrategy) {
        var headers = (Map<String, Object>) message.get(1);
        var serializeAsBinary = Objects.equals(true, headers.remove("_serializeAsBinary"));
        var forceSendJson = Objects.equals(true, headers.remove("_serializeAsJson"));
        if (serializeAsBinary && !forceSendJson) {
            try {
                var encodedMessage = binaryEncodingStrategy.encode(message);
                return serializationStrategy.toMsgPack(encodedMessage);
            } catch (BinaryEncoderUnavailableError e) {
                // We can still submit as json
                return serializationStrategy.toJson(message);
            }
        } else {
            return serializationStrategy.toJson(message);
        }
    }

    static List<Object> deserialize(byte[] messageBytes, SerializationStrategy serializationStrategy,
            BinaryEncodingStrategy binaryEncodingStrategy) {
        if (messageBytes[0] == '[') {
            return serializationStrategy.fromJson(messageBytes);
        } else {
            var encodedMessage = serializationStrategy.fromMsgPack(messageBytes);
            try {
                return binaryEncodingStrategy.decode(encodedMessage);
            } catch (BinaryEncoderUnavailableError e) {
                throw new DeserializationError(e);
            }
        }
    }

    static List<Object> serverBinaryEncode(List<Object> message, BinaryEncoder binaryEncoder) {
        var headers = (Map<String, Object>) message.get(1);

        var clientKnownBinaryChecksums = (List<Long>) headers.remove("_clientKnownBinaryChecksums");

        if (clientKnownBinaryChecksums == null || !clientKnownBinaryChecksums.contains(binaryEncoder.checksum)) {
            headers.put("_enc", binaryEncoder.encodeMap);
        }

        headers.put("_bin", List.of(binaryEncoder.checksum));

        return encode(message, binaryEncoder);
    }

    static List<Object> serverBinaryDecode(List<Object> message, BinaryEncoder binaryEncoder)
            throws BinaryEncoderUnavailableError {
        var headers = (Map<String, Object>) message.get(1);

        var clientKnownBinaryChecksums = (List<Long>) headers.get("_bin");

        var binaryChecksumUsedByClientOnThisMessage = clientKnownBinaryChecksums.get(0);

        if (!Objects.equals(binaryChecksumUsedByClientOnThisMessage, binaryEncoder.checksum)) {
            throw new BinaryEncoderUnavailableError();
        }

        return decode(message, binaryEncoder);
    }

    static List<Object> clientBinaryEncode(List<Object> message, Deque<BinaryEncoder> recentBinaryEncoders)
            throws BinaryEncoderUnavailableError {
        var headers = (Map<String, Object>) message.get(1);

        var checksums = recentBinaryEncoders.stream().map(be -> be.checksum).toList();
        headers.put("_bin", checksums);

        BinaryEncoder binaryEncoder;
        try {
            binaryEncoder = recentBinaryEncoders.getFirst();
        } catch (NoSuchElementException e) {
            throw new BinaryEncoderUnavailableError();
        }

        return encode(message, binaryEncoder);
    }

    static List<Object> clientBinaryDecode(List<Object> message, Deque<BinaryEncoder> recentBinaryEncoders)
            throws BinaryEncoderUnavailableError {
        var headers = (Map<String, Object>) message.get(1);

        var binaryChecksums = (List<Long>) headers.get("_bin");
        var binaryChecksum = binaryChecksums.get(0);

        // If there is a binary encoding included on this message, cache it
        if (headers.containsKey("_enc")) {
            var initialBinaryEncoding = (Map<String, Object>) headers.get("_enc");
            // Ensure everything is a long
            var binaryEncoding = initialBinaryEncoding.entrySet().stream()
                    .collect(Collectors.toMap(e -> e.getKey(), e -> {
                        var value = e.getValue();
                        if (value instanceof Integer i) {
                            return Long.valueOf(i);
                        } else if (value instanceof Long l) {
                            return l;
                        } else {
                            throw new RuntimeException("Unexpected type");
                        }
                    }));
            var newBinaryEncoder = new BinaryEncoder(binaryEncoding, binaryChecksum);
            recentBinaryEncoders.add(newBinaryEncoder);

            // We need to maintain 2 binary encodings in case a server is undergoing an API
            // change during a new jAPI deployment
            if (recentBinaryEncoders.size() >= 3) {
                recentBinaryEncoders.removeLast();
            }
        }

        var binaryEncoder = findBinaryEncoder(binaryChecksum, recentBinaryEncoders);
        if (!binaryEncoder.isPresent()) {
            throw new BinaryEncoderUnavailableError();
        }

        return decode(message, binaryEncoder.get());
    }

    private static Optional<BinaryEncoder> findBinaryEncoder(Long checksum, Deque<BinaryEncoder> binaryEncoderStore) {
        for (var binaryEncoder : binaryEncoderStore) {
            if (Objects.equals(binaryEncoder.checksum, checksum)) {
                return Optional.of(binaryEncoder);
            }
        }
        return Optional.empty();
    }

    private static List<Object> encode(List<Object> jApiMessage, BinaryEncoder binaryEncoder) {
        var decodedMessageType = jApiMessage.get(0);
        var encodedMessageType = get(decodedMessageType, binaryEncoder.encodeMap);
        var headers = (Map<String, Object>) jApiMessage.get(1);
        var encodedBody = encodeKeys(jApiMessage.get(2), binaryEncoder);
        return List.of(encodedMessageType, headers, encodedBody);
    }

    static List<Object> decode(List<Object> jApiMessage, BinaryEncoder binaryEncoder) {
        var encodedMessageType = jApiMessage.get(0);
        if (encodedMessageType instanceof Integer i) {
            encodedMessageType = Long.valueOf(i);
        }
        var decodedMessageType = get(encodedMessageType, binaryEncoder.decodeMap);
        var headers = (Map<String, Object>) jApiMessage.get(1);
        var givenChecksums = (List<Long>) headers.get("_bin");
        var decodedBody = decodeKeys(jApiMessage.get(2), binaryEncoder);
        // if (this.checksum != null && !givenChecksums.contains(this.checksum)) {
        // throw new BinaryChecksumMismatchException();
        // }
        return List.of(decodedMessageType, headers, decodedBody);
    }

    private static Object encodeKeys(Object given, BinaryEncoder binaryEncoder) {
        if (given == null) {
            return given;
        } else if (given instanceof Map<?, ?> m) {
            var newMap = new HashMap<>();
            m.entrySet().stream().forEach(e -> {
                var key = e.getKey();
                if (binaryEncoder.encodeMap.containsKey(key)) {
                    key = get(key, binaryEncoder.encodeMap);
                }
                var encodedValue = encodeKeys(e.getValue(), binaryEncoder);
                newMap.put(key, encodedValue);
            });
            return newMap;
        } else if (given instanceof List<?> l) {
            return l.stream().map(e -> encodeKeys(e, binaryEncoder)).toList();
        } else {
            return given;
        }
    }

    private static Object decodeKeys(Object given, BinaryEncoder binaryEncoder) {
        if (given instanceof Map<?, ?> m) {
            var newMap = new HashMap<>();
            m.entrySet().stream().forEach(e -> {
                var key = e.getKey();
                if (binaryEncoder.decodeMap.containsKey(key)) {
                    key = get(key, binaryEncoder.decodeMap);
                }
                var encodedValue = decodeKeys(e.getValue(), binaryEncoder);
                newMap.put(key, encodedValue);
            });
            return newMap;
        } else if (given instanceof List<?> l) {
            return l.stream().map(e -> decodeKeys(e, binaryEncoder)).toList();
        } else {
            return given;
        }
    }

    private static Object get(Object key, Map<?, ?> map) {
        var value = map.get(key);
        if (value == null) {
            throw new BinaryEncoderMissingEncoding(key);
        }
        return value;
    }
}
