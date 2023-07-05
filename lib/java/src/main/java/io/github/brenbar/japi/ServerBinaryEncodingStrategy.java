package io.github.brenbar.japi;

import java.util.List;

public class ServerBinaryEncodingStrategy implements BinaryEncodingStrategy {

    private BinaryEncoder binaryEncoder;

    public ServerBinaryEncodingStrategy(BinaryEncoder binaryEncoder) {
        this.binaryEncoder = binaryEncoder;
    }

    @Override
    public List<Object> encode(List<Object> message) {
        return InternalSerialize.serverBinaryEncode(message, binaryEncoder);
    }

    @Override
    public List<Object> decode(List<Object> message) throws BinaryEncoderUnavailableError {
        return InternalSerialize.serverBinaryDecode(message, binaryEncoder);
    }

}
