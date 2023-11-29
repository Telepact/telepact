package io.github.brenbar.japi;

import java.util.Deque;
import java.util.List;
import java.util.concurrent.ConcurrentLinkedDeque;

class _ClientBinaryEncoder implements BinaryEncoder {

    private Deque<BinaryEncoding> recentBinaryEncoders = new ConcurrentLinkedDeque<>();

    @Override
    public List<Object> encode(List<Object> message) throws BinaryEncoderUnavailableError {
        return _SerializerUtil.clientBinaryEncode(message, recentBinaryEncoders);
    }

    @Override
    public List<Object> decode(List<Object> message) throws BinaryEncoderUnavailableError {
        return _SerializerUtil.clientBinaryDecode(message, recentBinaryEncoders);
    }

}
