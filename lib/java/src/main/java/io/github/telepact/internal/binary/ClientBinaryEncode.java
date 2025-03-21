package io.github.telepact.internal.binary;

import static io.github.telepact.internal.binary.EncodeBody.encodeBody;
import static io.github.telepact.internal.binary.PackBody.packBody;

import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

import io.github.telepact.ClientBinaryStrategy;

public class ClientBinaryEncode {
    static List<Object> clientBinaryEncode(List<Object> message, Map<Integer, BinaryEncoding> recentBinaryEncoders,
            ClientBinaryStrategy binaryChecksumStrategy)
            throws BinaryEncoderUnavailableError {
        final var headers = (Map<String, Object>) message.get(0);
        final var messageBody = (Map<String, Object>) message.get(1);
        final var forceSendJson = headers.remove("_forceSendJson");

        headers.put("bin_", binaryChecksumStrategy.getCurrentChecksums());

        if (Objects.equals(forceSendJson, true)) {
            throw new BinaryEncoderUnavailableError();
        }

        if (recentBinaryEncoders.size() > 1) {
            throw new BinaryEncoderUnavailableError();
        }

        final Optional<BinaryEncoding> binaryEncoderOptional = recentBinaryEncoders.values().stream().findAny();
        if (!binaryEncoderOptional.isPresent()) {
            throw new BinaryEncoderUnavailableError();
        }
        final BinaryEncoding binaryEncoder = binaryEncoderOptional.get();

        final var encodedMessageBody = encodeBody(messageBody, binaryEncoder);

        final Map<Object, Object> finalEncodedMessageBody;
        if (Objects.equals(true, headers.get("pac_"))) {
            finalEncodedMessageBody = packBody(encodedMessageBody);
        } else {
            finalEncodedMessageBody = encodedMessageBody;
        }

        return List.of(headers, finalEncodedMessageBody);
    }
}
