package io.github.brenbar.uapi;

/**
 * Indicates failure to decode a binary uAPI message due to an unknown binary
 * field id that has no associated JSON key.
 */
public class BinaryEncodingMissing extends RuntimeException {

    public BinaryEncodingMissing(Object key) {
        super("Missing binary encoding for %s".formatted(String.valueOf(key)));
    }

}
