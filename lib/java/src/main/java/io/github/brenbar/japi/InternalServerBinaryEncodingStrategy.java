package io.github.brenbar.japi;

import java.util.List;

class InternalServerBinaryEncodingStrategy implements BinaryEncodingStrategy {

    private BinaryEncoder binaryEncoder;

    public InternalServerBinaryEncodingStrategy(BinaryEncoder binaryEncoder) {
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
