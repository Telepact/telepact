package io.github.telepact.internal.binary;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

public class DefaultBinaryEncodingCache implements BinaryEncodingCache {

    private final Map<Integer, BinaryEncoding> recentBinaryEncoders;

    public DefaultBinaryEncodingCache() {
        this.recentBinaryEncoders = new HashMap<>();
    }

    public void add(int checksum, Map<String, Integer> binaryEncodingMap) {
        BinaryEncoding binaryEncoding = new BinaryEncoding(binaryEncodingMap, checksum);
        this.recentBinaryEncoders.put(checksum, binaryEncoding);
    }

    public Optional<BinaryEncoding> get(int checksum) {
        if (!this.recentBinaryEncoders.containsKey(checksum)) {
            return Optional.empty();
        }
        return Optional.of(this.recentBinaryEncoders.get(checksum));
    }

    public void remove(int checksum) {
        this.recentBinaryEncoders.remove(checksum);
    }
}
