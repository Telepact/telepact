package io.github.brenbar.uapi;

import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.TreeSet;

class _SerializeUtil {

    static BinaryEncoding constructBinaryEncoding(UApiSchema uApiSchema) {
        final var allKeys = new TreeSet<String>();
        for (final var entry : uApiSchema.parsed.entrySet()) {
            allKeys.add(entry.getKey());

            if (entry.getValue() instanceof final _UStruct s) {
                final Map<String, _UFieldDeclaration> structFields = s.fields;
                allKeys.addAll(structFields.keySet());
            } else if (entry.getValue() instanceof final _UUnion u) {
                final Map<String, _UStruct> unionCases = u.cases;
                for (final var entry2 : unionCases.entrySet()) {
                    allKeys.add(entry2.getKey());
                    final var struct = entry2.getValue();
                    final var structFields = struct.fields;
                    allKeys.addAll(structFields.keySet());
                }
            } else if (entry.getValue() instanceof final _UFn f) {
                final _UUnion fnCall = f.call;
                final Map<String, _UStruct> fnCallCases = fnCall.cases;
                final _UUnion fnResult = f.result;
                final Map<String, _UStruct> fnResultCases = fnResult.cases;

                for (final var e2 : fnCallCases.entrySet()) {
                    allKeys.add(e2.getKey());
                    final var struct = e2.getValue();
                    final Map<String, _UFieldDeclaration> structFields = struct.fields;
                    allKeys.addAll(structFields.keySet());
                }

                for (var e2 : fnResultCases.entrySet()) {
                    allKeys.add(e2.getKey());
                    var struct = e2.getValue();
                    final Map<String, _UFieldDeclaration> structFields = struct.fields;
                    allKeys.addAll(structFields.keySet());
                }
            }
        }
        var i = 0;
        final var binaryEncoding = new HashMap<String, Integer>();
        for (final var key : allKeys) {
            binaryEncoding.put(key, i);
            i += 1;
        }
        final var finalString = String.join("\n", allKeys);
        final int checksum;
        try {
            final var hash = MessageDigest.getInstance("SHA-256").digest(finalString.getBytes(StandardCharsets.UTF_8));
            final var buffer = ByteBuffer.wrap(hash);
            checksum = buffer.getInt();
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        }
        return new BinaryEncoding(binaryEncoding, checksum);
    }

    static byte[] serialize(Message message, BinaryEncoder binaryEncoder,
            SerializationImpl serializer) {
        final var headers = message.header;

        final boolean serializeAsBinary;
        if (headers.containsKey("_binary")) {
            serializeAsBinary = Objects.equals(true, headers.remove("_binary"));
        } else {
            serializeAsBinary = false;
        }

        final List<Object> messageAsPseudoJson = List.of(message.header, message.body);
        if (serializeAsBinary) {
            try {
                final var encodedMessage = binaryEncoder.encode(messageAsPseudoJson);
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
        final Object messageAsPseudoJson;
        final boolean isMsgPack;
        if (messageBytes[0] == (byte) 0x92) { // MsgPack
            isMsgPack = true;
            messageAsPseudoJson = serializer.fromMsgPack(messageBytes);
        } else {
            isMsgPack = false;
            messageAsPseudoJson = serializer.fromJson(messageBytes);
        }

        final List<Object> messageAsPseudoJsonList;
        try {
            messageAsPseudoJsonList = _CastUtil.asList(messageAsPseudoJson);
        } catch (ClassCastException e) {
            throw new DeserializationError("ExpectedArrayOfTwoObjects");
        }

        if (messageAsPseudoJsonList.size() != 2) {
            throw new DeserializationError("ExpectedArrayOfTwoObjects");
        }

        final List<Object> finalMessageAsPseudoJsonList;
        if (isMsgPack) {
            try {
                finalMessageAsPseudoJsonList = binaryEncoder.decode(messageAsPseudoJsonList);
            } catch (Exception e) {
                throw new DeserializationError(e);
            }
        } else {
            finalMessageAsPseudoJsonList = messageAsPseudoJsonList;
        }

        Map<String, Object> headers = null;
        Map<String, Object> body = null;

        try {
            headers = _CastUtil.asMap(finalMessageAsPseudoJsonList.get(0));
        } catch (ClassCastException e) {
            throw new DeserializationError("ExpectedArrayOfTwoObjects");
        }

        try {
            body = _CastUtil.asMap(finalMessageAsPseudoJsonList.get(1));
            if (body.size() != 1) {
                throw new DeserializationError("ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject");
            } else {
                try {
                    var givenPayload = _CastUtil.asMap(body.values().stream().findAny().get());
                } catch (ClassCastException e) {
                    throw new DeserializationError("ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject");
                }
            }
        } catch (ClassCastException e) {
            throw new DeserializationError("ExpectedArrayOfTwoObjects");
        }

        return new Message(headers, body);
    }
}
