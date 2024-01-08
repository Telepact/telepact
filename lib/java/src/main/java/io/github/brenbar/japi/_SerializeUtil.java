package io.github.brenbar.japi;

import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.TreeSet;

class _SerializeUtil {

    static BinaryEncoding constructBinaryEncoding(JApiSchema jApiSchema) {
        var allKeys = new TreeSet<String>();
        for (var entry : jApiSchema.parsed.entrySet()) {
            allKeys.add(entry.getKey());
            if (entry.getValue() instanceof UStruct s) {
                allKeys.addAll(s.fields.keySet());
            } else if (entry.getValue() instanceof UUnion e) {
                for (var entry2 : e.values.entrySet()) {
                    allKeys.add(entry2.getKey());
                    var struct = entry2.getValue();
                    allKeys.addAll(struct.fields.keySet());
                }
            } else if (entry.getValue() instanceof UFn f) {
                for (var e2 : f.call.values.entrySet()) {
                    allKeys.add(e2.getKey());
                    var struct = e2.getValue();
                    allKeys.addAll(struct.fields.keySet());
                }
                for (var e2 : f.result.values.entrySet()) {
                    allKeys.add(e2.getKey());
                    var struct = e2.getValue();
                    allKeys.addAll(struct.fields.keySet());
                }
            }
        }
        var i = 0;
        var binaryEncoding = new HashMap<String, Integer>();
        for (var key : allKeys) {
            binaryEncoding.put(key, i++);
        }
        var finalString = String.join("\n", allKeys);
        int checksum;
        try {
            var hash = MessageDigest.getInstance("SHA-256").digest(finalString.getBytes(StandardCharsets.UTF_8));
            var buffer = ByteBuffer.wrap(hash);
            checksum = buffer.getInt();
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        }
        return new BinaryEncoding(binaryEncoding, checksum);
    }

    static byte[] serialize(Message message, BinaryEncoder binaryEncoder,
            SerializationImpl serializer) {
        var headers = message.header;
        boolean serializeAsBinary = headers.containsKey("_bin");
        if (headers.containsKey("_binary")) {
            serializeAsBinary = Objects.equals(true, headers.remove("_binary"));
        }
        List<Object> messageAsPseudoJson = List.of(message.header, message.body);
        if (serializeAsBinary) {
            try {
                var encodedMessage = binaryEncoder.encode(messageAsPseudoJson);
                return serializer.toMsgPack(encodedMessage);
            } catch (BinaryEncoderUnavailableError e) {
                // We can still submit as json
                return serializer.toJson(messageAsPseudoJson);
            }
        } else {
            return serializer.toJson(messageAsPseudoJson);
        }
    }

    static Message deserialize(byte[] messageBytes, SerializationImpl serializer,
            BinaryEncoder binaryEncoder) {
        Object messageAsPseudoJson;
        boolean isMsgPack = false;
        if (messageBytes[0] == (byte) 0x92) { // MsgPack
            isMsgPack = true;
            messageAsPseudoJson = serializer.fromMsgPack(messageBytes);
        } else {
            messageAsPseudoJson = serializer.fromJson(messageBytes);
        }

        List<Object> messageAsPseudoJsonList;
        try {
            messageAsPseudoJsonList = (List<Object>) messageAsPseudoJson;
        } catch (ClassCastException e) {
            throw new DeserializationError(new MessageParseError(List.of("MessageMustBeArrayWithTwoElements")));
        }

        if (messageAsPseudoJsonList.size() != 2) {
            throw new DeserializationError(new MessageParseError(List.of("MessageMustBeArrayWithTwoElements")));
        }

        List<Object> finalMessageAsPseudoJsonList;
        if (isMsgPack) {
            try {
                finalMessageAsPseudoJsonList = binaryEncoder.decode(messageAsPseudoJsonList);
            } catch (Exception e) {
                throw new DeserializationError(e);
            }
        } else {
            finalMessageAsPseudoJsonList = messageAsPseudoJsonList;
        }

        var parseFailures = new ArrayList<String>();
        Map<String, Object> headers = null;
        Map<String, Object> body = null;

        try {
            headers = (Map<String, Object>) finalMessageAsPseudoJsonList.get(0);
        } catch (ClassCastException e) {
            parseFailures.add("HeadersMustBeObject");
        }

        try {
            body = (Map<String, Object>) finalMessageAsPseudoJsonList.get(1);
            if (body.size() != 1) {
                parseFailures.add("BodyMustBeUnionType");
            } else {
                try {
                    var givenPayload = (Map<String, Object>) body.values().stream().findAny().get();
                } catch (ClassCastException e) {
                    parseFailures.add("BodyPayloadMustBeObject");
                }
            }
        } catch (ClassCastException e) {
            parseFailures.add("BodyMustBeObject");
        }

        if (parseFailures.size() > 0) {
            throw new DeserializationError(new MessageParseError(parseFailures));
        }

        return new Message(headers, body);
    }
}
