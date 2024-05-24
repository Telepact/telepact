package io.github.brenbar.uapi.internal;

import java.util.List;
import java.util.Map;

import io.github.brenbar.uapi.Message;
import io.github.brenbar.uapi.SerializationImpl;
import io.github.brenbar.uapi.internal.binary.BinaryEncoder;

import static io.github.brenbar.uapi.internal.AsList.asList;
import static io.github.brenbar.uapi.internal.AsMap.asMap;

public class DeserializeInternal {

    public static Message deserializeInternal(byte[] messageBytes, SerializationImpl serializer,
            BinaryEncoder binaryEncoder) {
        final Object messageAsPseudoJson;
        final boolean isMsgPack;

        try {
            if (messageBytes[0] == (byte) 0x92) { // MsgPack
                isMsgPack = true;
                messageAsPseudoJson = serializer.fromMsgPack(messageBytes);
            } else {
                isMsgPack = false;
                messageAsPseudoJson = serializer.fromJson(messageBytes);
            }
        } catch (Throwable e) {
            throw new InvalidMessage(e);
        }

        final List<Object> messageAsPseudoJsonList;
        try {
            messageAsPseudoJsonList = asList(messageAsPseudoJson);
        } catch (ClassCastException e) {
            throw new InvalidMessage();
        }

        if (messageAsPseudoJsonList.size() != 2) {
            throw new InvalidMessage();
        }

        final List<Object> finalMessageAsPseudoJsonList;
        if (isMsgPack) {
            finalMessageAsPseudoJsonList = binaryEncoder.decode(messageAsPseudoJsonList);
        } else {
            finalMessageAsPseudoJsonList = messageAsPseudoJsonList;
        }

        Map<String, Object> headers = null;
        Map<String, Object> body = null;

        try {
            headers = asMap(finalMessageAsPseudoJsonList.get(0));
        } catch (ClassCastException e) {
            throw new InvalidMessage();
        }

        try {
            body = asMap(finalMessageAsPseudoJsonList.get(1));
            if (body.size() != 1) {
                throw new InvalidMessageBody();
            } else {
                try {
                    var givenPayload = asMap(body.values().stream().findAny().get());
                } catch (ClassCastException e) {
                    throw new InvalidMessageBody();
                }
            }
        } catch (ClassCastException e) {
            throw new InvalidMessage();
        }

        return new Message(headers, body);
    }
}
