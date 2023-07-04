package io.github.brenbar.japi;

import java.util.List;
import java.util.Map;
import java.util.Objects;

public class ServerBinaryEncoderStrategy implements BinaryEncodingStrategy {

    private BinaryEncoder binaryEncoder;

    public ServerBinaryEncoderStrategy(BinaryEncoder binaryEncoder) {
        this.binaryEncoder = binaryEncoder;
    }

    @Override
    public List<Object> encode(List<Object> message) {
        var headers = (Map<String, Object>) message.get(1);

        var clientKnownChecksums = (List<Long>) headers.remove("_clientKnownBinaryChecksums");
        if (clientKnownChecksums == null || !clientKnownChecksums.contains(binaryEncoder.checksum)) {
            headers.put("_binaryEncoding", this.binaryEncoder.encodeMap);
        }

        return this.binaryEncoder.encode(message);
    }

    @Override
    public List<Object> decode(List<Object> message) throws BinaryEncoderUnavailableError {
        var headers = (Map<String, Object>) message.get(1);

        var binaryChecksums = (List<Long>) headers.get("_bin");
        headers.put("_clientKnownBinaryChecksums", binaryChecksums);

        var binaryChecksum = binaryChecksums.get(0);

        if (!Objects.equals(binaryChecksum, this.binaryEncoder.checksum)) {
            throw new BinaryEncoderUnavailableError();
        }

        return this.binaryEncoder.decode(message);
    }

}
