package io.github.brenbar.japi;

import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Deque;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.NoSuchElementException;
import java.util.Objects;
import java.util.Optional;
import java.util.TreeSet;
import java.util.stream.Collectors;

class _SerializerUtil {

    static BinaryEncoding constructBinaryEncoding(JApiSchema jApiSchema) {
        var allKeys = new TreeSet<String>();
        for (var entry : jApiSchema.parsed.entrySet()) {
            allKeys.add(entry.getKey());
            if (entry.getValue() instanceof UStruct s) {
                allKeys.addAll(s.fields.keySet());
            } else if (entry.getValue() instanceof UEnum e) {
                for (var entry2 : e.values.entrySet()) {
                    allKeys.add(entry2.getKey());
                    var struct = entry2.getValue();
                    allKeys.addAll(struct.fields.keySet());
                }
            } else if (entry.getValue() instanceof UFn f) {
                allKeys.addAll(f.arg.fields.keySet());
                for (var e2 : f.result.values.entrySet()) {
                    allKeys.add(e2.getKey());
                    var struct = e2.getValue();
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
        int checksum;
        try {
            var hash = MessageDigest.getInstance("SHA-256").digest(finalString.getBytes(StandardCharsets.UTF_8));
            var buffer = ByteBuffer.wrap(hash);
            checksum = buffer.getInt();
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        }
        return new BinaryEncoding(binaryEncoding, checksum);
    }

    static byte[] serialize(Message message, BinaryEncoder binaryEncoder,
            SerializationImpl serializer) {
        var headers = message.header;
        boolean serializeAsBinary = false;
        if (headers.containsKey("_binary")) {
            serializeAsBinary = Objects.equals(true, headers.remove("_binary"));
        }
        List<Object> messageAsPseudoJson = List.of(message.header, message.body);
        if (serializeAsBinary) {
            try {
                var encodedMessage = binaryEncoder.encode(messageAsPseudoJson);
                return serializer.toMsgPack(encodedMessage);
            } catch (BinaryEncoderUnavailableError e) {
                // We can still submit as json
                return serializer.toJson(messageAsPseudoJson);
            }
        } else {
            return serializer.toJson(messageAsPseudoJson);
        }
    }

    static Message deserialize(byte[] messageBytes, SerializationImpl serializer,
            BinaryEncoder binaryEncoder) {
        Object messageAsPseudoJson;
        boolean isMsgPack = false;
        if (messageBytes[0] == (byte) 0x92) { // MsgPack
            isMsgPack = true;
            messageAsPseudoJson = serializer.fromMsgPack(messageBytes);
        } else {
            messageAsPseudoJson = serializer.fromJson(messageBytes);
        }

        List<Object> messageAsPseudoJsonList;
        try {
            messageAsPseudoJsonList = (List<Object>) messageAsPseudoJson;
        } catch (ClassCastException e) {
            throw new DeserializationError(new MessageParseError(List.of("MessageMustBeArrayWithTwoElements")));
        }

        if (messageAsPseudoJsonList.size() != 2) {
            throw new DeserializationError(new MessageParseError(List.of("MessageMustBeArrayWithTwoElements")));
        }

        List<Object> finalMessageAsPseudoJsonList;
        if (isMsgPack) {
            try {
                finalMessageAsPseudoJsonList = binaryEncoder.decode(messageAsPseudoJsonList);
            } catch (Exception e) {
                throw new DeserializationError(e);
            }
        } else {
            finalMessageAsPseudoJsonList = messageAsPseudoJsonList;
        }

        var parseFailures = new ArrayList<String>();
        Map<String, Object> headers = null;
        Map<String, Object> body = null;

        try {
            headers = (Map<String, Object>) finalMessageAsPseudoJsonList.get(0);
        } catch (ClassCastException e) {
            parseFailures.add("HeadersMustBeObject");
        }

        try {
            body = (Map<String, Object>) finalMessageAsPseudoJsonList.get(1);
            if (body.size() != 1) {
                parseFailures.add("BodyMustBeUnionType");
            } else {
                try {
                    var givenPayload = (Map<String, Object>) body.values().stream().findAny().get();
                } catch (ClassCastException e) {
                    parseFailures.add("BodyPayloadMustBeObject");
                }
            }
        } catch (ClassCastException e) {
            parseFailures.add("BodyMustBeObject");
        }

        if (parseFailures.size() > 0) {
            throw new DeserializationError(new MessageParseError(parseFailures));
        }

        return new Message(headers, body);
    }

    static List<Object> serverBinaryEncode(List<Object> message, BinaryEncoding binaryEncoder) {
        var headers = (Map<String, Object>) message.get(0);

        var clientKnownBinaryChecksums = (List<Integer>) headers.remove("_clientKnownBinaryChecksums");

        if (clientKnownBinaryChecksums == null || !clientKnownBinaryChecksums.contains(binaryEncoder.checksum)) {
            headers.put("_enc", binaryEncoder.encodeMap);
        }

        headers.put("_bin", List.of(binaryEncoder.checksum));

        var messageBody = (Map<String, Object>) message.get(1);

        var encodedMessageBody = encode(messageBody, binaryEncoder);

        return List.of(headers, encodedMessageBody);
    }

    static List<Object> serverBinaryDecode(List<Object> message, BinaryEncoding binaryEncoder)
            throws BinaryEncoderUnavailableError {
        var headers = (Map<String, Object>) message.get(0);

        var clientKnownBinaryChecksums = (List<Integer>) headers.get("_bin");

        var binaryChecksumUsedByClientOnThisMessage = clientKnownBinaryChecksums.get(0);

        if (!Objects.equals(binaryChecksumUsedByClientOnThisMessage, binaryEncoder.checksum)) {
            throw new BinaryEncoderUnavailableError();
        }

        var encodedMessageBody = (Map<Object, Object>) message.get(1);

        var messageBody = decode(encodedMessageBody, binaryEncoder);

        return List.of(headers, messageBody);
    }

    static List<Object> clientBinaryEncode(List<Object> message, Deque<BinaryEncoding> recentBinaryEncoders)
            throws BinaryEncoderUnavailableError {
        var headers = (Map<String, Object>) message.get(0);

        var checksums = recentBinaryEncoders.stream().map(be -> be.checksum).toList();
        headers.put("_bin", checksums);

        BinaryEncoding binaryEncoder;
        try {
            binaryEncoder = recentBinaryEncoders.getFirst();
        } catch (NoSuchElementException e) {
            throw new BinaryEncoderUnavailableError();
        }

        var messageBody = (Map<String, Object>) message.get(1);

        var encodedMessageBody = encode(messageBody, binaryEncoder);

        return List.of(headers, encodedMessageBody);
    }

    static List<Object> clientBinaryDecode(List<Object> message, Deque<BinaryEncoding> recentBinaryEncoders)
            throws BinaryEncoderUnavailableError {
        var headers = (Map<String, Object>) message.get(0);

        var binaryChecksums = (List<Integer>) headers.get("_bin");
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
            var newBinaryEncoder = new BinaryEncoding(binaryEncoding, binaryChecksum);
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

    private static Optional<BinaryEncoding> findBinaryEncoder(Integer checksum,
            Deque<BinaryEncoding> binaryEncoderStore) {
        for (var binaryEncoder : binaryEncoderStore) {
            if (Objects.equals(binaryEncoder.checksum, checksum)) {
                return Optional.of(binaryEncoder);
            }
        }
        return Optional.empty();
    }

    private static Map<Object, Object> encode(Map<String, Object> messageBody, BinaryEncoding binaryEncoder) {
        var encodedMessageBody = (Map<Object, Object>) encodeKeys(messageBody, binaryEncoder);
        return encodedMessageBody;
    }

    static Map<String, Object> decode(Map<Object, Object> encodedMessageBody, BinaryEncoding binaryEncoder) {
        return (Map<String, Object>) decodeKeys(encodedMessageBody, binaryEncoder);
        // TODO: move this logic somewhere else
        // if (this.checksum != null && !givenChecksums.contains(this.checksum)) {
        // throw new BinaryChecksumMismatchException();
        // }
    }

    private static Object encodeKeys(Object given, BinaryEncoding binaryEncoder) {
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

    private static Object decodeKeys(Object given, BinaryEncoding binaryEncoder) {
        if (given instanceof Map<?, ?> m) {
            var newMap = new HashMap<String, Object>();
            m.entrySet().stream().forEach(e -> {
                String key;
                if (e.getKey() instanceof String s) {
                    key = s;
                } else {
                    key = (String) get(e.getKey(), binaryEncoder.decodeMap);
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
            throw new BinaryEncodingMissing(key);
        }
        return value;
    }
}
