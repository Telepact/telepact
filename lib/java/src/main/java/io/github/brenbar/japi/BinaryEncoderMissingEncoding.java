package io.github.brenbar.japi;

public class BinaryEncoderMissingEncoding extends RuntimeException {

    public BinaryEncoderMissingEncoding(Object key) {
        super("Missing binary encoding for %s".formatted(String.valueOf(key)));
    }

}
