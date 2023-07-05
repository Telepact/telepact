package io.github.brenbar.japi;

import java.util.Deque;
import java.util.List;
import java.util.concurrent.ConcurrentLinkedDeque;

class ClientBinaryEncodingStrategy implements BinaryEncodingStrategy {

    private Deque<BinaryEncoder> recentBinaryEncoders = new ConcurrentLinkedDeque<>();

    @Override
    public List<Object> encode(List<Object> message) throws BinaryEncoderUnavailableError {
        return InternalBinaryEncode.clientBinaryEncode(message, recentBinaryEncoders);
    }

    @Override
    public List<Object> decode(List<Object> message) throws BinaryEncoderUnavailableError {
        return InternalBinaryEncode.clientBinaryDecode(message, recentBinaryEncoders);
    }

}
