package io.github.brenbar.japi;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

class _BinaryEncodeUtil {

    static List<Object> serverBinaryEncode(List<Object> message, BinaryEncoding binaryEncoder) {
        var headers = (Map<String, Object>) message.get(0);

        var clientKnownBinaryChecksums = (List<Integer>) headers.remove("_clientKnownBinaryChecksums");

        if (clientKnownBinaryChecksums == null || !clientKnownBinaryChecksums.contains(binaryEncoder.checksum)) {
            headers.put("_enc", binaryEncoder.encodeMap);
        }

        headers.put("_bin", List.of(binaryEncoder.checksum));

        var messageBody = (Map<String, Object>) message.get(1);

        var encodedMessageBody = encode(messageBody, binaryEncoder);

        if (Objects.equals(true, headers.get("_pac"))) {
            encodedMessageBody = _BinaryPackUtil.packBody(encodedMessageBody);
        }

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

        if (Objects.equals(true, headers.get("_pac"))) {
            encodedMessageBody = _BinaryPackUtil.unpackBody(encodedMessageBody);
        }

        var messageBody = decode(encodedMessageBody, binaryEncoder);

        return List.of(headers, messageBody);
    }

    static List<Object> clientBinaryEncode(List<Object> message, Map<Integer, BinaryEncoding> recentBinaryEncoders,
            BinaryChecksumStrategy binaryChecksumStrategy)
            throws BinaryEncoderUnavailableError {
        var headers = (Map<String, Object>) message.get(0);

        headers.put("_bin", binaryChecksumStrategy.get());

        var forceSendJson = headers.remove("_forceSendJson");

        if (Objects.equals(forceSendJson, true)) {
            throw new BinaryEncoderUnavailableError();
        }

        if (recentBinaryEncoders.size() > 1) {
            // Can't know which encoder to use.
            throw new BinaryEncoderUnavailableError();
        }

        var checksums = recentBinaryEncoders.keySet().stream().toList();

        BinaryEncoding binaryEncoder;
        try {
            binaryEncoder = recentBinaryEncoders.get(checksums.get(0));
        } catch (ArrayIndexOutOfBoundsException e) {
            throw new BinaryEncoderUnavailableError();
        }

        var messageBody = (Map<String, Object>) message.get(1);

        var encodedMessageBody = encode(messageBody, binaryEncoder);

        if (Objects.equals(true, headers.get("_pac"))) {
            encodedMessageBody = _BinaryPackUtil.packBody(encodedMessageBody);
        }

        return List.of(headers, encodedMessageBody);
    }

    static List<Object> clientBinaryDecode(List<Object> message, Map<Integer, BinaryEncoding> recentBinaryEncoders,
            BinaryChecksumStrategy binaryChecksumStrategy)
            throws BinaryEncoderUnavailableError {
        var headers = (Map<String, Object>) message.get(0);

        var binaryChecksums = (List<Integer>) headers.get("_bin");
        var binaryChecksum = binaryChecksums.get(0);

        // If there is a binary encoding included on this message, cache it
        if (headers.containsKey("_enc")) {
            var binaryEncoding = (Map<String, Integer>) headers.get("_enc");
            var newBinaryEncoder = new BinaryEncoding(binaryEncoding, binaryChecksum);
            recentBinaryEncoders.put(binaryChecksum, newBinaryEncoder);
        }

        binaryChecksumStrategy.update(binaryChecksum);
        List<Integer> newCurrentChecksumStrategy = binaryChecksumStrategy.get();
        recentBinaryEncoders.entrySet().removeIf(e -> !newCurrentChecksumStrategy.contains(e.getKey()));

        var binaryEncoder = recentBinaryEncoders.get(binaryChecksum);

        var encodedMessageBody = (Map<Object, Object>) message.get(1);

        if (Objects.equals(true, headers.get("_pac"))) {
            encodedMessageBody = _BinaryPackUtil.unpackBody(encodedMessageBody);
        }

        var messageBody = decode(encodedMessageBody, binaryEncoder);

        return List.of(headers, messageBody);
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
