package io.github.brenbar.uapi;

import java.util.List;

class _ServerBinaryEncoder implements _BinaryEncoder {

    private final _BinaryEncoding binaryEncoder;

    public _ServerBinaryEncoder(_BinaryEncoding binaryEncoder) {
        this.binaryEncoder = binaryEncoder;
    }

    @Override
    public List<Object> encode(List<Object> message) {
        return _BinaryEncodeUtil.serverBinaryEncode(message, binaryEncoder);
    }

    @Override
    public List<Object> decode(List<Object> message) throws BinaryEncoderUnavailableError {
        return _BinaryEncodeUtil.serverBinaryDecode(message, binaryEncoder);
    }

}
