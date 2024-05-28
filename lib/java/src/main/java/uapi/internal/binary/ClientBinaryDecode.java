package uapi.internal.binary;

import static uapi.internal.binary.DecodeBody.decodeBody;
import static uapi.internal.binary.UnpackBody.unpackBody;

import java.util.List;
import java.util.Map;
import java.util.Objects;

import uapi.ClientBinaryStrategy;

public class ClientBinaryDecode {
    static List<Object> clientBinaryDecode(List<Object> message, Map<Integer, BinaryEncoding> recentBinaryEncoders,
            ClientBinaryStrategy binaryChecksumStrategy)
            throws BinaryEncoderUnavailableError {
        final var headers = (Map<String, Object>) message.get(0);
        final var encodedMessageBody = (Map<Object, Object>) message.get(1);
        final var binaryChecksums = (List<Integer>) headers.get("bin_");
        final var binaryChecksum = binaryChecksums.get(0);

        // If there is a binary encoding included on this message, cache it
        if (headers.containsKey("enc_")) {
            final var binaryEncoding = (Map<String, Integer>) headers.get("enc_");
            final var newBinaryEncoder = new BinaryEncoding(binaryEncoding, binaryChecksum);

            recentBinaryEncoders.put(binaryChecksum, newBinaryEncoder);
        }

        binaryChecksumStrategy.update(binaryChecksum);
        final var newCurrentChecksumStrategy = binaryChecksumStrategy.getCurrentChecksums();

        recentBinaryEncoders.entrySet().removeIf(e -> !newCurrentChecksumStrategy.contains(e.getKey()));
        final var binaryEncoder = recentBinaryEncoders.get(binaryChecksum);

        final Map<Object, Object> finalEncodedMessageBody;
        if (Objects.equals(true, headers.get("_pac"))) {
            finalEncodedMessageBody = unpackBody(encodedMessageBody);
        } else {
            finalEncodedMessageBody = encodedMessageBody;
        }

        final var messageBody = decodeBody(finalEncodedMessageBody, binaryEncoder);
        return List.of(headers, messageBody);
    }
}
