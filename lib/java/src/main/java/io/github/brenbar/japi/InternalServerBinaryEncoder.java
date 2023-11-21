package io.github.brenbar.japi;

import java.util.List;

class InternalServerBinaryEncoder implements BinaryEncoder {

    private BinaryEncoding binaryEncoder;

    public InternalServerBinaryEncoder(BinaryEncoding binaryEncoder) {
        this.binaryEncoder = binaryEncoder;
    }

    @Override
    public List<Object> encode(List<Object> message) {
        return InternalSerializer.serverBinaryEncode(message, binaryEncoder);
    }

    @Override
    public List<Object> decode(List<Object> message) throws BinaryEncoderUnavailableError {
        return InternalSerializer.serverBinaryDecode(message, binaryEncoder);
    }

}
