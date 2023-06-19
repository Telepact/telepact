package io.github.brenbar.japi;

import java.util.List;
import java.util.Map;
import java.util.function.Consumer;

class ProcessBytes {

    static byte[] process(byte[] inputJapiMessagePayload, Serializer serializer, Consumer<Throwable> onError,
            BinaryEncoder binaryEncoder, Map<String, Definition> apiDescription, Handler internalHandler,
            Handler handler) {
        List<Object> inputJapiMessage;
        boolean inputIsBinary = false;
        if (inputJapiMessagePayload[0] == '[') {
            try {
                inputJapiMessage = serializer.deserializeFromJson(inputJapiMessagePayload);
            } catch (DeserializationError e) {
                onError.accept(e);
                return serializer.serializeToJson(List.of("error._ParseFailure", Map.of(), Map.of()));
            }
        } else {
            try {
                var encodedInputJapiMessage = serializer.deserializeFromMsgPack(inputJapiMessagePayload);
                if (encodedInputJapiMessage.size() < 3) {
                    return serializer.serializeToJson(List.of("error._ParseFailure", Map.of(),
                            Map.of("reason", "JapiMessageArrayMustHaveThreeElements")));
                }
                inputJapiMessage = binaryEncoder.decode(encodedInputJapiMessage);
                inputIsBinary = true;
            } catch (IncorrectBinaryHashException e) {
                onError.accept(e);
                return serializer.serializeToJson(List.of("error._InvalidBinaryEncoding", Map.of(), Map.of()));
            } catch (DeserializationError e) {
                onError.accept(e);
                return serializer.serializeToJson(List.of("error._ParseFailure", Map.of(), Map.of()));
            }
        }

        var outputJapiMessage = ProcessObject.process(inputJapiMessage, onError, binaryEncoder, apiDescription,
                internalHandler, handler);
        var headers = (Map<String, Object>) outputJapiMessage.get(1);
        var returnAsBinary = headers.containsKey("_bin");
        if (!returnAsBinary && inputIsBinary) {
            headers.put("_bin", binaryEncoder.binaryHash);
        }

        if (inputIsBinary || returnAsBinary) {
            var encodedOutputJapiMessage = binaryEncoder.encode(outputJapiMessage);
            return serializer.serializeToMsgPack(encodedOutputJapiMessage);
        } else {
            return serializer.serializeToJson(outputJapiMessage);
        }
    }
}
