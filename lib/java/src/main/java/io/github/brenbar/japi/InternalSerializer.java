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
            if (entry.getValue() instanceof Struct s) {
                allKeys.addAll(s.fields.keySet());
            } else if (entry.getValue() instanceof Enum e) {
                for (var entry2 : e.values.entrySet()) {
                    allKeys.add(entry2.getKey());
                    var struct = entry2.getValue();
                    allKeys.addAll(struct.fields.keySet());
                }
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

    static byte[] serialize(Message message, BinaryEncodingStrategy binaryEncodingStrategy,
            SerializationStrategy serializationStrategy) {
        var headers = message.header;
        boolean serializeAsBinary = false;
        if (headers.containsKey("_serializeAsBinary")) {
            serializeAsBinary = Objects.equals(true, headers.remove("_serializeAsBinary"));
        }
        boolean forceSendJson = false;
        if (headers.containsKey("_serializeAsJson")) {
            forceSendJson = Objects.equals(true, headers.remove("_serializeAsJson"));
        }
        List<Object> messageAsPseudoJson = List.of(message.header, message.body);
        if (serializeAsBinary && !forceSendJson) {
            try {
                var encodedMessage = binaryEncodingStrategy.encode(messageAsPseudoJson);
                return serializationStrategy.toMsgPack(encodedMessage);
            } catch (BinaryEncoderUnavailableError e) {
                // We can still submit as json
                return serializationStrategy.toJson(messageAsPseudoJson);
            }
        } else {
            return serializationStrategy.toJson(messageAsPseudoJson);
        }
    }

    static Message deserialize(byte[] messageBytes, SerializationStrategy serializationStrategy,
            BinaryEncodingStrategy binaryEncodingStrategy) {
        if (messageBytes[0] == '[') {
            var messageAsPseudoJson = serializationStrategy.fromJson(messageBytes);
            var header = (Map<String, Object>) messageAsPseudoJson.get(0);
            var body = (Map<String, Object>) messageAsPseudoJson.get(1);
            return new Message(header, body);
        } else {
            var encodedMessage = serializationStrategy.fromMsgPack(messageBytes);
            List<Object> messageAsPseudoJson;
            try {
                messageAsPseudoJson = binaryEncodingStrategy.decode(encodedMessage);
            } catch (BinaryEncoderUnavailableError e) {
                throw new DeserializationError(e);
            }
            var header = (Map<String, Object>) messageAsPseudoJson.get(0);
            var body = (Map<String, Object>) messageAsPseudoJson.get(1);
            return new Message(header, body);
        }
    }

    static List<Object> serverBinaryEncode(List<Object> message, BinaryEncoder binaryEncoder) {
        var headers = (Map<String, Object>) message.get(0);

        var clientKnownBinaryChecksums = (List<Long>) headers.remove("_clientKnownBinaryChecksums");

        if (clientKnownBinaryChecksums == null || !clientKnownBinaryChecksums.contains(binaryEncoder.checksum)) {
            headers.put("_enc", binaryEncoder.encodeMap);
        }

        headers.put("_bin", List.of(binaryEncoder.checksum));

        var messageBody = (Map<String, Object>) message.get(1);

        var encodedMessageBody = encode(messageBody, binaryEncoder);

        return List.of(headers, encodedMessageBody);
    }

    static List<Object> serverBinaryDecode(List<Object> message, BinaryEncoder binaryEncoder)
            throws BinaryEncoderUnavailableError {
        var headers = (Map<String, Object>) message.get(0);

        var clientKnownBinaryChecksums = (List<Long>) headers.get("_bin");

        var binaryChecksumUsedByClientOnThisMessage = clientKnownBinaryChecksums.get(0);

        if (!Objects.equals(binaryChecksumUsedByClientOnThisMessage, binaryEncoder.checksum)) {
            throw new BinaryEncoderUnavailableError();
        }

        var encodedMessageBody = (Map<Object, Object>) message.get(1);

        var messageBody = decode(encodedMessageBody, binaryEncoder);

        return List.of(headers, messageBody);
    }

    static List<Object> clientBinaryEncode(List<Object> message, Deque<BinaryEncoder> recentBinaryEncoders)
            throws BinaryEncoderUnavailableError {
        var headers = (Map<String, Object>) message.get(0);

        var checksums = recentBinaryEncoders.stream().map(be -> be.checksum).toList();
        headers.put("_bin", checksums);

        BinaryEncoder binaryEncoder;
        try {
            binaryEncoder = recentBinaryEncoders.getFirst();
        } catch (NoSuchElementException e) {
            throw new BinaryEncoderUnavailableError();
        }

        var messageBody = (Map<String, Object>) message.get(1);

        var encodedMessageBody = encode(messageBody, binaryEncoder);

        return List.of(headers, encodedMessageBody);
    }

    static List<Object> clientBinaryDecode(List<Object> message, Deque<BinaryEncoder> recentBinaryEncoders)
            throws BinaryEncoderUnavailableError {
        var headers = (Map<String, Object>) message.get(0);

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

        var encodedMessageBody = (Map<Object, Object>) message.get(1);

        var messageBody = decode(encodedMessageBody, binaryEncoder.get());

        return List.of(headers, messageBody);
    }

    private static Optional<BinaryEncoder> findBinaryEncoder(Long checksum, Deque<BinaryEncoder> binaryEncoderStore) {
        for (var binaryEncoder : binaryEncoderStore) {
            if (Objects.equals(binaryEncoder.checksum, checksum)) {
                return Optional.of(binaryEncoder);
            }
        }
        return Optional.empty();
    }

    private static Map<Object, Object> encode(Map<String, Object> messageBody, BinaryEncoder binaryEncoder) {
        var encodedMessageBody = (Map<Object, Object>) encodeKeys(messageBody, binaryEncoder);
        return encodedMessageBody;
    }

    static Map<String, Object> decode(Map<Object, Object> encodedMessageBody, BinaryEncoder binaryEncoder) {
        return (Map<String, Object>) decodeKeys(encodedMessageBody, binaryEncoder);
        // TODO: move this logic somewhere else
        // if (this.checksum != null && !givenChecksums.contains(this.checksum)) {
        // throw new BinaryChecksumMismatchException();
        // }
    }

    private static Object encodeKeys(Object given, BinaryEncoder binaryEncoder) {
        if (given == null) {
            return given;
        } else if (given instanceof Map<?, ?> m) {
            var newMap = new HashMap<Object, Object>();
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
            var newMap = new HashMap<String, Object>();
            m.entrySet().stream().forEach(e -> {
                var key = (String) get(e.getKey(), binaryEncoder.decodeMap);
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
