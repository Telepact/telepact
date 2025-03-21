package io.github.telepact.internal.binary;

public class BinaryEncodingMissing extends RuntimeException {

    public BinaryEncodingMissing(Object key) {
        super("Missing binary encoding for %s".formatted(String.valueOf(key)));
    }

}
