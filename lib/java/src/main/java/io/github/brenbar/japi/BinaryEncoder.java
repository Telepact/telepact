package io.github.brenbar.japi;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.stream.Collectors;

class BinaryEncoder {

    public final Map<String, Long> encodeMap;
    public final Map<Long, String> decodeMap;
    public final Long checksum;

    public BinaryEncoder(Map<String, Long> binaryEncoding, Long binaryHash) {
        this.encodeMap = binaryEncoding;
        this.decodeMap = binaryEncoding.entrySet().stream()
                .collect(Collectors.toMap(e -> Long.valueOf(e.getValue()), e -> e.getKey()));
        this.checksum = binaryHash;
    }

    public List<Object> encode(List<Object> japiMessage) {
        var encodedMessageType = get(encodeMap, japiMessage.get(0));
        var headers = (Map<String, Object>) japiMessage.get(1);
        var encodedBody = encodeKeys(japiMessage.get(2));
        return List.of(encodedMessageType, headers, encodedBody);
    }

    public List<Object> decode(List<Object> japiMessage) {
        var encodedMessageType = japiMessage.get(0);
        if (encodedMessageType instanceof Integer i) {
            encodedMessageType = Long.valueOf(i);
        }
        var decodedMessageType = get(decodeMap, encodedMessageType);
        var headers = (Map<String, Object>) japiMessage.get(1);
        var givenChecksums = (List<Long>) headers.get("_bin");
        var decodedBody = decodeKeys(japiMessage.get(2));
        // if (this.checksum != null && !givenChecksums.contains(this.checksum)) {
        // throw new BinaryChecksumMismatchException();
        // }
        return List.of(decodedMessageType, headers, decodedBody);
    }

    private Object encodeKeys(Object given) {
        if (given == null) {
            return given;
        } else if (given instanceof Map<?, ?> m) {
            var newMap = new HashMap<>();
            m.entrySet().stream().forEach(e -> {
                var key = e.getKey();
                if (encodeMap.containsKey(key)) {
                    key = get(encodeMap, key);
                }
                var encodedValue = encodeKeys(e.getValue());
                newMap.put(key, encodedValue);
            });
            return newMap;
        } else if (given instanceof List<?> l) {
            return l.stream().map(e -> encodeKeys(e)).toList();
        } else {
            return given;
        }
    }

    private Object decodeKeys(Object given) {
        if (given instanceof Map<?, ?> m) {
            var newMap = new HashMap<>();
            m.entrySet().stream().forEach(e -> {
                var key = e.getKey();
                if (decodeMap.containsKey(key)) {
                    key = get(decodeMap, key);
                }
                var encodedValue = decodeKeys(e.getValue());
                newMap.put(key, encodedValue);
            });
            return newMap;
        } else if (given instanceof List<?> l) {
            return l.stream().map(e -> decodeKeys(e)).toList();
        } else {
            return given;
        }
    }

    private Object get(Map<?, ?> map, Object key) {
        var value = map.get(key);
        if (value == null) {
            throw new RuntimeException("Missing encoding for " + String.valueOf(key));
        }
        return value;
    }
}
