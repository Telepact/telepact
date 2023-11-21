package io.github.brenbar.japi;

import java.util.Deque;
import java.util.List;
import java.util.concurrent.ConcurrentLinkedDeque;

class InternalClientBinaryEncoder implements BinaryEncoder {

    private Deque<BinaryEncoding> recentBinaryEncoders = new ConcurrentLinkedDeque<>();

    @Override
    public List<Object> encode(List<Object> message) throws BinaryEncoderUnavailableError {
        return InternalSerializer.clientBinaryEncode(message, recentBinaryEncoders);
    }

    @Override
    public List<Object> decode(List<Object> message) throws BinaryEncoderUnavailableError {
        return InternalSerializer.clientBinaryDecode(message, recentBinaryEncoders);
    }

}
