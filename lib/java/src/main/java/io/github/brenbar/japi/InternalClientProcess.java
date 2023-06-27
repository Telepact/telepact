package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.Deque;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.function.BiFunction;
import java.util.function.Function;
import java.util.stream.Collectors;

public class InternalClientProcess {

    static Map<String, Object> call(
            Request request,
            BiFunction<List<Object>, Boolean, List<Object>> serializeAndTransport,
            Function<Map<String, Object>, Map<String, Object>> modifyHeaders,
            BiFunction<List<Object>, Function<List<Object>, List<Object>>, List<Object>> middleware,
            Deque<BinaryEncoder> recentBinaryEncoders,
            boolean useBinaryDefault,
            boolean forceSendJsonDefault) {

        var headers = modifyHeaders.apply(request.headers);

        if (!request.selectedStructFields.isEmpty()) {
            headers.put("_selectFields", request.selectedStructFields);
        }

        boolean finalUseBinary;
        if (request.useBinary.isPresent()) {
            finalUseBinary = request.useBinary.get();
        } else {
            finalUseBinary = useBinaryDefault;
        }

        boolean finalForceSendJson;
        if (request.forceSendJson.isPresent()) {
            finalForceSendJson = request.forceSendJson.get();
        } else {
            finalForceSendJson = forceSendJsonDefault;
        }

        if (finalUseBinary) {
            List<Object> binaryChecksums = new ArrayList<>();
            for (var binaryEncoding : recentBinaryEncoders) {
                binaryChecksums.add(binaryEncoding.checksum);
            }
            headers.put("_bin", binaryChecksums);
        }

        var messageType = "function.%s".formatted(request.functionName);
        var inputJapiMessage = List.of(messageType, headers, request.functionInput);

        var outputJapiMessage = encodeSerializeAndTransport(inputJapiMessage, serializeAndTransport, middleware,
                recentBinaryEncoders, finalUseBinary, finalForceSendJson);

        var outputMessageType = (String) outputJapiMessage.get(0);
        var output = (Map<String, Object>) outputJapiMessage.get(2);

        if (outputMessageType.startsWith("error.")) {
            throw new JApiError(outputMessageType, output);
        }

        return output;
    }

    private static List<Object> encodeSerializeAndTransport(List<Object> inputJapiMessage,
            BiFunction<List<Object>, Boolean, List<Object>> serializeAndTransport,
            BiFunction<List<Object>, Function<List<Object>, List<Object>>, List<Object>> middleware,
            Deque<BinaryEncoder> recentBinaryEncoders,
            boolean useBinary,
            boolean forceSendJson) {
        try {
            var binaryEncoder = recentBinaryEncoders.size() == 0 ? null : recentBinaryEncoders.getFirst();

            boolean sendAsMsgPack = false;
            List<Object> finalInputJapiMessage;
            if (forceSendJson || !useBinary || binaryEncoder == null) {
                finalInputJapiMessage = inputJapiMessage;
            } else {
                finalInputJapiMessage = binaryEncoder.encode(inputJapiMessage);
                sendAsMsgPack = true;
            }

            var outputJapiMessage = serializeAndTransport.apply(finalInputJapiMessage, sendAsMsgPack);
            var outputHeaders = (Map<String, Object>) outputJapiMessage.get(1);

            // If the response is in binary, decode it
            if (outputHeaders.containsKey("_bin")) {
                var binaryChecksum = (List<Long>) outputHeaders.get("_bin");

                if (outputHeaders.containsKey("_binaryEncoding")) {
                    var initialBinaryEncoding = (Map<String, Object>) outputHeaders.get("_binaryEncoding");
                    // Ensure everything is a long
                    var binaryEncoding = initialBinaryEncoding.entrySet().stream()
                            .collect(Collectors.toMap(e -> e.getKey(), e -> {
                                var value = e.getValue();
                                if (value instanceof Integer i) {
                                    return Long.valueOf(i);
                                } else if (value instanceof Long l) {
                                    return l;
                                } else {
                                    throw new RuntimeException("Unexpected type");
                                }
                            }));
                    var newBinaryEncoder = new BinaryEncoder(binaryEncoding, binaryChecksum.get(0));
                    recentBinaryEncoders.add(newBinaryEncoder);

                    // We need to maintain 2 binary encodings in case a server is undergoing an API
                    // change during a new jAPI deployment
                    if (recentBinaryEncoders.size() >= 3) {
                        recentBinaryEncoders.removeLast();
                    }
                }

                var outputBinaryEncoder = findBinaryEncoder(recentBinaryEncoders, binaryChecksum.get(0));

                return outputBinaryEncoder.decode(outputJapiMessage);
            }

            return outputJapiMessage;
        } catch (Exception e) {
            throw new ClientProcessError(e);
        }
    }

    private static BinaryEncoder findBinaryEncoder(Deque<BinaryEncoder> binaryEncoderStore, Long checksum) {
        for (var binaryEncoder : binaryEncoderStore) {
            if (Objects.equals(binaryEncoder.checksum, checksum)) {
                return binaryEncoder;
            }
        }
        throw new ClientProcessError(
                new Exception("No matching encoding found for checksum %d, cannot decode binary".formatted(checksum)));
    }

    static byte[] serialize(List<Object> jApiMessage, Serializer serializer, boolean sendAsMsgPack) {
        if (sendAsMsgPack) {
            return serializer.serializeToMsgPack(jApiMessage);
        } else {
            return serializer.serializeToJson(jApiMessage);
        }
    }

    static List<Object> deserialize(byte[] jApiMessageBytes, Serializer serializer) {
        try {
            if (jApiMessageBytes[0] == '[') {
                return serializer.deserializeFromJson(jApiMessageBytes);
            } else {
                return serializer.deserializeFromMsgPack(jApiMessageBytes);
            }
        } catch (DeserializationException e) {
            throw new ClientProcessError(e);
        }
    }
}
