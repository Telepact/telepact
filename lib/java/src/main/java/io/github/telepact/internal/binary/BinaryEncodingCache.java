package io.github.telepact.internal.binary;

import java.util.Map;
import java.util.Optional;

public interface BinaryEncodingCache {

    /**
     * Set a binary encoding in the cache.
     * @param checksum The checksum of the binary encoding.
     * @param binaryEncodingMap The binary encoding map.
     */
    void add(int checksum, Map<String, Integer> binaryEncodingMap);

    /**
     * Get a binary encoding from the cache.
     * @param checksum The checksum of the binary encoding.
     * @return The binary encoding.
     */
    Optional<BinaryEncoding> get(int checksum);

    /**
     * Delete a binary encoding from the cache.
     * @param checksum The checksum of the binary encoding.
     */
    void remove(int checksum);
}
