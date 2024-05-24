package io.github.brenbar.uapi.internal;

import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

import io.github.brenbar.uapi.ClientBinaryStrategy;

import static io.github.brenbar.uapi.internal.EncodeBody.encodeBody;
import static io.github.brenbar.uapi.internal.PackBody.packBody;

public class ClientBinaryEncode {
    static List<Object> clientBinaryEncode(List<Object> message, Map<Integer, _BinaryEncoding> recentBinaryEncoders,
            ClientBinaryStrategy binaryChecksumStrategy)
            throws _BinaryEncoderUnavailableError {
        final var headers = (Map<String, Object>) message.get(0);
        final var messageBody = (Map<String, Object>) message.get(1);
        final var forceSendJson = headers.remove("_forceSendJson");

        headers.put("bin_", binaryChecksumStrategy.getCurrentChecksums());

        if (Objects.equals(forceSendJson, true)) {
            throw new _BinaryEncoderUnavailableError();
        }

        if (recentBinaryEncoders.size() > 1) {
            throw new _BinaryEncoderUnavailableError();
        }

        final Optional<_BinaryEncoding> binaryEncoderOptional = recentBinaryEncoders.values().stream().findAny();
        if (!binaryEncoderOptional.isPresent()) {
            throw new _BinaryEncoderUnavailableError();
        }
        final _BinaryEncoding binaryEncoder = binaryEncoderOptional.get();

        final var encodedMessageBody = encodeBody(messageBody, binaryEncoder);

        final Map<Object, Object> finalEncodedMessageBody;
        if (Objects.equals(true, headers.get("_pac"))) {
            finalEncodedMessageBody = packBody(encodedMessageBody);
        } else {
            finalEncodedMessageBody = encodedMessageBody;
        }

        return List.of(headers, finalEncodedMessageBody);
    }
}
