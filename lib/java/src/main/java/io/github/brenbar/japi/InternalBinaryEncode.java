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

class InternalBinaryEncode {

    static BinaryEncoder build(Map<String, Definition> definitions) {
        var allKeys = new TreeSet<String>();
        for (var entry : definitions.entrySet()) {
            allKeys.add(entry.getKey());
            if (entry.getValue() instanceof FunctionDefinition f) {
                allKeys.addAll(f.inputStruct.fields.keySet());
                allKeys.addAll(f.outputStruct.fields.keySet());
                allKeys.addAll(f.allowedErrors);
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

    static List<Object> serverBinaryEncode(List<Object> message, BinaryEncoder binaryEncoder) {
        var headers = (Map<String, Object>) message.get(1);

        var clientKnownChecksums = (List<Long>) headers.remove("_clientKnownBinaryChecksums");

        if (clientKnownChecksums == null || !clientKnownChecksums.contains(binaryEncoder.checksum)) {
            headers.put("_enc", binaryEncoder.encodeMap);
        }

        headers.put("_bin", List.of(binaryEncoder.checksum));

        return encode(message, binaryEncoder);
    }

    static List<Object> serverBinaryDecode(List<Object> message, BinaryEncoder binaryEncoder)
            throws BinaryEncoderUnavailableError {
        var headers = (Map<String, Object>) message.get(1);

        var binaryChecksums = (List<Long>) headers.get("_bin");
        headers.put("_clientKnownBinaryChecksums", binaryChecksums);

        var binaryChecksum = binaryChecksums.get(0);

        if (!Objects.equals(binaryChecksum, binaryEncoder.checksum)) {
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

        var binaryEncoder = findBinaryEncoder(recentBinaryEncoders, binaryChecksum);
        if (!binaryEncoder.isPresent()) {
            throw new BinaryEncoderUnavailableError();
        }

        return decode(message, binaryEncoder.get());
    }

    private static Optional<BinaryEncoder> findBinaryEncoder(Deque<BinaryEncoder> binaryEncoderStore, Long checksum) {
        for (var binaryEncoder : binaryEncoderStore) {
            if (Objects.equals(binaryEncoder.checksum, checksum)) {
                return Optional.of(binaryEncoder);
            }
        }
        return Optional.empty();
    }

    private static List<Object> encode(List<Object> japiMessage, BinaryEncoder binaryEncoder) {
        var encodedMessageType = get(binaryEncoder.encodeMap, japiMessage.get(0));
        var headers = (Map<String, Object>) japiMessage.get(1);
        var encodedBody = encodeKeys(japiMessage.get(2), binaryEncoder);
        return List.of(encodedMessageType, headers, encodedBody);
    }

    static List<Object> decode(List<Object> japiMessage, BinaryEncoder binaryEncoder) {
        var encodedMessageType = japiMessage.get(0);
        if (encodedMessageType instanceof Integer i) {
            encodedMessageType = Long.valueOf(i);
        }
        var decodedMessageType = get(binaryEncoder.decodeMap, encodedMessageType);
        var headers = (Map<String, Object>) japiMessage.get(1);
        var givenChecksums = (List<Long>) headers.get("_bin");
        var decodedBody = decodeKeys(japiMessage.get(2), binaryEncoder);
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
                    key = get(binaryEncoder.encodeMap, key);
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
                    key = get(binaryEncoder.decodeMap, key);
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

    private static Object get(Map<?, ?> map, Object key) {
        var value = map.get(key);
        if (value == null) {
            throw new RuntimeException("Missing encoding for " + String.valueOf(key));
        }
        return value;
    }
}
