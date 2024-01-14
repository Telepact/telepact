package io.github.brenbar.japi;

import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

class _ClientBinaryEncoder implements BinaryEncoder {

    private Map<Integer, BinaryEncoding> recentBinaryEncoders;
    private BinaryChecksumStrategy binaryChecksumStrategy;

    public _ClientBinaryEncoder(BinaryChecksumStrategy binaryChecksumStrategy) {
        this.recentBinaryEncoders = new ConcurrentHashMap<>();
        this.binaryChecksumStrategy = binaryChecksumStrategy;
    }

    @Override
    public List<Object> encode(List<Object> message) throws BinaryEncoderUnavailableError {
        return _BinaryEncodeUtil.clientBinaryEncode(message, recentBinaryEncoders,
                binaryChecksumStrategy);
    }

    @Override
    public List<Object> decode(List<Object> message) throws BinaryEncoderUnavailableError {
        return _BinaryEncodeUtil.clientBinaryDecode(message, recentBinaryEncoders, binaryChecksumStrategy);
    }

}
