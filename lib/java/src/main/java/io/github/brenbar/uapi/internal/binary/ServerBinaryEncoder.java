package io.github.brenbar.uapi.internal.binary;

import static io.github.brenbar.uapi.internal.binary.ServerBinaryDecode.serverBinaryDecode;
import static io.github.brenbar.uapi.internal.binary.ServerBinaryEncode.serverBinaryEncode;

import java.util.List;

public class ServerBinaryEncoder implements BinaryEncoder {

    private final BinaryEncoding binaryEncoder;

    public ServerBinaryEncoder(BinaryEncoding binaryEncoder) {
        this.binaryEncoder = binaryEncoder;
    }

    @Override
    public List<Object> encode(List<Object> message) {
        return serverBinaryEncode(message, binaryEncoder);
    }

    @Override
    public List<Object> decode(List<Object> message) {
        return serverBinaryDecode(message, binaryEncoder);
    }

}
