package io.github.brenbar.japi;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.stream.Collectors;

class BinaryEncoder {

    public final Map<String, Long> encodeMap;
    public final Map<Long, String> decodeMap;
    public final Object binaryHash;

    public BinaryEncoder(Map<String, Long> binaryEncoding, Object binaryHash) {
        this.encodeMap = binaryEncoding;
        this.decodeMap = binaryEncoding.entrySet().stream()
                .collect(Collectors.toMap(e -> Long.valueOf(e.getValue()), e -> e.getKey()));
        this.binaryHash = binaryHash;
    }

    public List<Object> encode(List<Object> japiMessage) {
        var encodedMessageType = get(encodeMap, japiMessage.get(0));
        var headers = japiMessage.get(1);
        var encodedBody = encodeKeys(japiMessage.get(2));
        return List.of(encodedMessageType, headers, encodedBody);
    }

    public List<Object> decode(List<Object> japiMessage) throws IncorrectBinaryHashException {
        var encodedMessageType = japiMessage.get(0);
        if (encodedMessageType instanceof Integer i) {
            encodedMessageType = Long.valueOf(i);
        }
        var decodedMessageType = get(decodeMap, encodedMessageType);
        var headers = (Map<String, Object>) japiMessage.get(1);
        var givenHash = (Long) headers.get("_bin");
        var decodedBody = decodeKeys(japiMessage.get(2));
        if (binaryHash != null && !Objects.equals(givenHash, binaryHash)) {
            throw new IncorrectBinaryHashException();
        }
        return List.of(decodedMessageType, headers, decodedBody);
    }

    private Object encodeKeys(Object given) {
        if (given == null) {
            return given;
        } else if (given instanceof Map<?, ?> m) {
            var newMap = new HashMap<>();
            m.entrySet().stream().forEach(e -> {
                // TODO: Update the msgpack library to not coerce these ints to strings
                // because now we have to coerce it back conditionally, since we
                // can't know for sure if somebody didn't just use a number string
                // in their generic object.
                var key = e.getKey();
                if (key instanceof String s) {
                    try {
                        key = Long.valueOf(s);
                    } catch (Exception ignored) {
                    }
                }
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
                // TODO: Update the msgpack library to not coerce these ints to strings
                // because now we have to coerce it back conditionally, since we
                // can't know for sure if somebody didn't just use a number string
                // in their generic object.
                var key = e.getKey();
                if (key instanceof String s) {
                    try {
                        key = Long.valueOf(s);
                    } catch (Exception ignored) {
                    }
                }
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
