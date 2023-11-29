package io.github.brenbar.japi;

import java.util.List;

class _ServerBinaryEncoder implements BinaryEncoder {

    private BinaryEncoding binaryEncoder;

    public _ServerBinaryEncoder(BinaryEncoding binaryEncoder) {
        this.binaryEncoder = binaryEncoder;
    }

    @Override
    public List<Object> encode(List<Object> message) {
        return _SerializerUtil.serverBinaryEncode(message, binaryEncoder);
    }

    @Override
    public List<Object> decode(List<Object> message) throws BinaryEncoderUnavailableError {
        return _SerializerUtil.serverBinaryDecode(message, binaryEncoder);
    }

}
