package io.github.brenbar.japi;

import java.util.List;

public interface BinaryEncodingStrategy {
    List<Object> encode(List<Object> message) throws BinaryEncoderUnavailableError;

    List<Object> decode(List<Object> message) throws BinaryEncoderUnavailableError;
}