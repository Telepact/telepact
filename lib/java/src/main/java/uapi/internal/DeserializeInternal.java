package uapi.internal;

import java.util.List;
import java.util.Map;

import uapi.Message;
import uapi.Serialization;
import uapi.internal.binary.BinaryEncoder;
import uapi.internal.validation.InvalidMessage;
import uapi.internal.validation.InvalidMessageBody;

public class DeserializeInternal {

    public static Message deserializeInternal(byte[] messageBytes, Serialization serialization,
            BinaryEncoder binaryEncoder) {
        final Object messageAsPseudoJson;
        final boolean isMsgPack;

        try {
            if (messageBytes[0] == (byte) 0x92) { // MsgPack
                isMsgPack = true;
                messageAsPseudoJson = serialization.fromMsgPack(messageBytes);
            } else {
                isMsgPack = false;
                messageAsPseudoJson = serialization.fromJson(messageBytes);
            }
        } catch (Throwable e) {
            throw new InvalidMessage(e);
        }

        if (!(messageAsPseudoJson instanceof List)) {
            throw new InvalidMessage();
        }
        final List<Object> messageAsPseudoJsonList = (List<Object>) messageAsPseudoJson;

        if (messageAsPseudoJsonList.size() != 2) {
            throw new InvalidMessage();
        }

        final List<Object> finalMessageAsPseudoJsonList;
        if (isMsgPack) {
            finalMessageAsPseudoJsonList = binaryEncoder.decode(messageAsPseudoJsonList);
        } else {
            finalMessageAsPseudoJsonList = messageAsPseudoJsonList;
        }

        if (!(finalMessageAsPseudoJsonList.get(0) instanceof Map)) {
            throw new InvalidMessage();
        }
        Map<String, Object> headers = (Map<String, Object>) finalMessageAsPseudoJsonList.get(0);

        if (!(finalMessageAsPseudoJsonList.get(1) instanceof Map)) {
            throw new InvalidMessage();
        }
        Map<String, Object> body = (Map<String, Object>) finalMessageAsPseudoJsonList.get(1);

        if (body.size() != 1) {
            throw new InvalidMessageBody();
        }

        if (!(body.values().stream().findAny().get() instanceof Map)) {
            throw new InvalidMessageBody();
        }

        return new Message(headers, body);
    }
}
