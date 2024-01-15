package io.github.brenbar.uapi;

import java.util.List;

class _ServerBinaryEncoder implements BinaryEncoder {

    private BinaryEncoding binaryEncoder;

    public _ServerBinaryEncoder(BinaryEncoding binaryEncoder) {
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
