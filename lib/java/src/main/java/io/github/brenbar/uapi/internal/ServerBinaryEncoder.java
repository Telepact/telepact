package io.github.brenbar.uapi.internal;

import java.util.List;

import static io.github.brenbar.uapi.internal.ServerBinaryDecode.serverBinaryDecode;
import static io.github.brenbar.uapi.internal.ServerBinaryEncode.serverBinaryEncode;

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
