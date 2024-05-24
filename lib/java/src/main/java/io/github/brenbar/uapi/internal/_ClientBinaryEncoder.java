package io.github.brenbar.uapi.internal;

import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import io.github.brenbar.uapi.ClientBinaryStrategy;

import static io.github.brenbar.uapi.internal.ClientBinaryEncode.clientBinaryEncode;
import static io.github.brenbar.uapi.internal.ClientBinaryDecode.clientBinaryDecode;

public class _ClientBinaryEncoder implements _BinaryEncoder {

    private final Map<Integer, _BinaryEncoding> recentBinaryEncoders;
    private final ClientBinaryStrategy binaryChecksumStrategy;

    public _ClientBinaryEncoder(ClientBinaryStrategy binaryChecksumStrategy) {
        this.recentBinaryEncoders = new ConcurrentHashMap<>();
        this.binaryChecksumStrategy = binaryChecksumStrategy;
    }

    @Override
    public List<Object> encode(List<Object> message) throws _BinaryEncoderUnavailableError {
        return clientBinaryEncode(message, this.recentBinaryEncoders,
                this.binaryChecksumStrategy);
    }

    @Override
    public List<Object> decode(List<Object> message) throws _BinaryEncoderUnavailableError {
        return clientBinaryDecode(message, this.recentBinaryEncoders, this.binaryChecksumStrategy);
    }

}