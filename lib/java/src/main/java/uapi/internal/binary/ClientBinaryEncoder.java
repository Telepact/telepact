package uapi.internal.binary;

import static uapi.internal.binary.ClientBinaryDecode.clientBinaryDecode;
import static uapi.internal.binary.ClientBinaryEncode.clientBinaryEncode;

import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import uapi.ClientBinaryStrategy;

public class ClientBinaryEncoder implements BinaryEncoder {

    private final Map<Integer, BinaryEncoding> recentBinaryEncoders;
    private final ClientBinaryStrategy binaryChecksumStrategy;

    public ClientBinaryEncoder(ClientBinaryStrategy binaryChecksumStrategy) {
        this.recentBinaryEncoders = new ConcurrentHashMap<>();
        this.binaryChecksumStrategy = binaryChecksumStrategy;
    }

    @Override
    public List<Object> encode(List<Object> message) throws BinaryEncoderUnavailableError {
        return clientBinaryEncode(message, this.recentBinaryEncoders,
                this.binaryChecksumStrategy);
    }

    @Override
    public List<Object> decode(List<Object> message) throws BinaryEncoderUnavailableError {
        return clientBinaryDecode(message, this.recentBinaryEncoders, this.binaryChecksumStrategy);
    }

}