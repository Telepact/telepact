package io.github.brenbar.uapi;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

class _BinaryEncodeUtil {

    static List<Object> serverBinaryEncode(List<Object> message, BinaryEncoding binaryEncoder) {
        final var headers = (Map<String, Object>) message.get(0);
        final var messageBody = (Map<String, Object>) message.get(1);
        final var clientKnownBinaryChecksums = (List<Integer>) headers.remove("_clientKnownBinaryChecksums");

        if (clientKnownBinaryChecksums == null || !clientKnownBinaryChecksums.contains(binaryEncoder.checksum)) {
            headers.put("_enc", binaryEncoder.encodeMap);
        }

        headers.put("_bin", List.of(binaryEncoder.checksum));
        final var encodedMessageBody = encodeBody(messageBody, binaryEncoder);

        final Map<Object, Object> finalEncodedMessageBody;
        if (Objects.equals(true, headers.get("_pac"))) {
            finalEncodedMessageBody = _BinaryPackUtil.packBody(encodedMessageBody);
        } else {
            finalEncodedMessageBody = encodedMessageBody;
        }

        return List.of(headers, finalEncodedMessageBody);
    }

    static List<Object> serverBinaryDecode(List<Object> message, BinaryEncoding binaryEncoder)
            throws BinaryEncoderUnavailableError {
        final var headers = (Map<String, Object>) message.get(0);
        final var encodedMessageBody = (Map<Object, Object>) message.get(1);
        final var clientKnownBinaryChecksums = (List<Integer>) headers.get("_bin");
        final var binaryChecksumUsedByClientOnThisMessage = clientKnownBinaryChecksums.get(0);

        if (!Objects.equals(binaryChecksumUsedByClientOnThisMessage, binaryEncoder.checksum)) {
            throw new BinaryEncoderUnavailableError();
        }

        final Map<Object, Object> finalEncodedMessageBody;
        if (Objects.equals(true, headers.get("_pac"))) {
            finalEncodedMessageBody = _BinaryPackUtil.unpackBody(encodedMessageBody);
        } else {
            finalEncodedMessageBody = encodedMessageBody;
        }

        final var messageBody = decodeBody(finalEncodedMessageBody, binaryEncoder);
        return List.of(headers, messageBody);
    }

    static List<Object> clientBinaryEncode(List<Object> message, Map<Integer, BinaryEncoding> recentBinaryEncoders,
            BinaryChecksumStrategy binaryChecksumStrategy)
            throws BinaryEncoderUnavailableError {
        final var headers = (Map<String, Object>) message.get(0);
        final var messageBody = (Map<String, Object>) message.get(1);
        final var forceSendJson = headers.remove("_forceSendJson");

        headers.put("_bin", binaryChecksumStrategy.get());

        if (Objects.equals(forceSendJson, true)) {
            throw new BinaryEncoderUnavailableError();
        }

        if (recentBinaryEncoders.size() > 1) {
            throw new BinaryEncoderUnavailableError();
        }

        final var checksums = recentBinaryEncoders.keySet().stream().toList();

        final BinaryEncoding binaryEncoder;
        try {
            binaryEncoder = recentBinaryEncoders.get(checksums.get(0));
        } catch (ArrayIndexOutOfBoundsException e) {
            throw new BinaryEncoderUnavailableError();
        }

        final var encodedMessageBody = encodeBody(messageBody, binaryEncoder);

        final Map<Object, Object> finalEncodedMessageBody;
        if (Objects.equals(true, headers.get("_pac"))) {
            finalEncodedMessageBody = _BinaryPackUtil.packBody(encodedMessageBody);
        } else {
            finalEncodedMessageBody = encodedMessageBody;
        }

        return List.of(headers, finalEncodedMessageBody);
    }

    static List<Object> clientBinaryDecode(List<Object> message, Map<Integer, BinaryEncoding> recentBinaryEncoders,
            BinaryChecksumStrategy binaryChecksumStrategy)
            throws BinaryEncoderUnavailableError {
        final var headers = (Map<String, Object>) message.get(0);
        final var encodedMessageBody = (Map<Object, Object>) message.get(1);
        final var binaryChecksums = (List<Integer>) headers.get("_bin");
        final var binaryChecksum = binaryChecksums.get(0);

        // If there is a binary encoding included on this message, cache it
        if (headers.containsKey("_enc")) {
            final var binaryEncoding = (Map<String, Integer>) headers.get("_enc");
            final var newBinaryEncoder = new BinaryEncoding(binaryEncoding, binaryChecksum);

            recentBinaryEncoders.put(binaryChecksum, newBinaryEncoder);
        }

        binaryChecksumStrategy.update(binaryChecksum);
        final var newCurrentChecksumStrategy = binaryChecksumStrategy.get();

        recentBinaryEncoders.entrySet().removeIf(e -> !newCurrentChecksumStrategy.contains(e.getKey()));
        final var binaryEncoder = recentBinaryEncoders.get(binaryChecksum);

        final Map<Object, Object> finalEncodedMessageBody;
        if (Objects.equals(true, headers.get("_pac"))) {
            finalEncodedMessageBody = _BinaryPackUtil.unpackBody(encodedMessageBody);
        } else {
            finalEncodedMessageBody = encodedMessageBody;
        }

        final var messageBody = decodeBody(finalEncodedMessageBody, binaryEncoder);
        return List.of(headers, messageBody);
    }

    private static Map<Object, Object> encodeBody(Map<String, Object> messageBody, BinaryEncoding binaryEncoder) {
        return (Map<Object, Object>) encodeKeys(messageBody, binaryEncoder);
    }

    static Map<String, Object> decodeBody(Map<Object, Object> encodedMessageBody, BinaryEncoding binaryEncoder) {
        return (Map<String, Object>) decodeKeys(encodedMessageBody, binaryEncoder);
    }

    private static Object encodeKeys(Object given, BinaryEncoding binaryEncoder) {
        if (given == null) {
            return given;
        } else if (given instanceof final Map<?, ?> m) {
            final var newMap = new HashMap<Object, Object>();

            for (final var e : m.entrySet()) {
                final var key = e.getKey();

                final Object finalKey;
                if (binaryEncoder.encodeMap.containsKey(key)) {
                    finalKey = get(key, binaryEncoder.encodeMap);
                } else {
                    finalKey = key;
                }

                final var encodedValue = encodeKeys(e.getValue(), binaryEncoder);

                newMap.put(finalKey, encodedValue);
            }

            return newMap;
        } else if (given instanceof List<?> l) {
            return l.stream().map(e -> encodeKeys(e, binaryEncoder)).toList();
        } else {
            return given;
        }
    }

    private static Object decodeKeys(Object given, BinaryEncoding binaryEncoder) {
        if (given instanceof Map<?, ?> m) {
            final var newMap = new HashMap<String, Object>();

            for (final var e : m.entrySet()) {
                final String key;
                if (e.getKey() instanceof final String s) {
                    key = s;
                } else {
                    key = (String) get(e.getKey(), binaryEncoder.decodeMap);
                }
                final var encodedValue = decodeKeys(e.getValue(), binaryEncoder);

                newMap.put(key, encodedValue);
            }

            return newMap;
        } else if (given instanceof final List<?> l) {
            return l.stream().map(e -> decodeKeys(e, binaryEncoder)).toList();
        } else {
            return given;
        }
    }

    private static Object get(Object key, Map<?, ?> map) {
        final var value = map.get(key);

        if (value == null) {
            throw new BinaryEncodingMissing(key);
        }

        return value;
    }

}
