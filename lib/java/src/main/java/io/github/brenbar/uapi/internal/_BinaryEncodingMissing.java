package io.github.brenbar.uapi.internal;

public class _BinaryEncodingMissing extends RuntimeException {

    public _BinaryEncodingMissing(Object key) {
        super("Missing binary encoding for %s".formatted(String.valueOf(key)));
    }

}
