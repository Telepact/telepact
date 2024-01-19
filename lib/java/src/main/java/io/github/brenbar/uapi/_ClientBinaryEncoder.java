package io.github.brenbar.uapi;

import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

class _ClientBinaryEncoder implements _BinaryEncoder {

    private final Map<Integer, _BinaryEncoding> recentBinaryEncoders;
    private final ClientBinaryStrategy binaryChecksumStrategy;

    public _ClientBinaryEncoder(ClientBinaryStrategy binaryChecksumStrategy) {
        this.recentBinaryEncoders = new ConcurrentHashMap<>();
        this.binaryChecksumStrategy = binaryChecksumStrategy;
    }

    @Override
    public List<Object> encode(List<Object> message) throws BinaryEncoderUnavailableError {
        return _BinaryEncodeUtil.clientBinaryEncode(message, this.recentBinaryEncoders,
                this.binaryChecksumStrategy);
    }

    @Override
    public List<Object> decode(List<Object> message) throws BinaryEncoderUnavailableError {
        return _BinaryEncodeUtil.clientBinaryDecode(message, this.recentBinaryEncoders, this.binaryChecksumStrategy);
    }

}
