package io.github.brenbar.uapi.internal;

import java.util.Map;
import java.util.stream.Collectors;

public class _BinaryEncoding {

    public final Map<String, Integer> encodeMap;
    public final Map<Integer, String> decodeMap;
    public final Integer checksum;

    public _BinaryEncoding(Map<String, Integer> binaryEncodingMap, Integer checksum) {
        this.encodeMap = binaryEncodingMap;
        this.decodeMap = binaryEncodingMap.entrySet().stream()
                .collect(Collectors.toMap(e -> e.getValue(), e -> e.getKey()));
        this.checksum = checksum;
    }
}