package io.github.msgpact.internal.binary;

import static io.github.msgpact.internal.binary.DecodeBody.decodeBody;
import static io.github.msgpact.internal.binary.UnpackBody.unpackBody;

import java.util.List;
import java.util.Map;
import java.util.Objects;

import io.github.msgpact.ClientBinaryStrategy;

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

        binaryChecksumStrategy.updateChecksum(binaryChecksum);
        final var newCurrentChecksumStrategy = binaryChecksumStrategy.getCurrentChecksums();

        recentBinaryEncoders.entrySet().removeIf(e -> !newCurrentChecksumStrategy.contains(e.getKey()));
        final var binaryEncoder = recentBinaryEncoders.get(binaryChecksum);

        final Map<Object, Object> finalEncodedMessageBody;
        if (Objects.equals(true, headers.get("pac_"))) {
            finalEncodedMessageBody = unpackBody(encodedMessageBody);
        } else {
            finalEncodedMessageBody = encodedMessageBody;
        }

        final var messageBody = decodeBody(finalEncodedMessageBody, binaryEncoder);
        return List.of(headers, messageBody);
    }
}
