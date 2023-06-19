package io.github.brenbar.japi.server;

import io.github.brenbar.japi.BinaryEncoder;
import io.github.brenbar.japi.Parser;
import io.github.brenbar.japi.Serializer;

import java.util.List;
import java.util.Map;
import java.util.function.Consumer;

class ProcessBytes {

    static byte[] process(byte[] inputJapiMessagePayload, Serializer serializer, Consumer<Throwable> onError, BinaryEncoder binaryEncoder, Map<String, Parser.Definition> apiDescription, Handler internalHandler, Handler handler) {
        List<Object> inputJapiMessage;
        boolean inputIsBinary = false;
        if (inputJapiMessagePayload[0] == '[') {
            try {
                inputJapiMessage = serializer.deserializeFromJson(inputJapiMessagePayload);
            } catch (Serializer.DeserializationError e) {
                onError.accept(e);
                return serializer.serializeToJson(List.of("error._ParseFailure", Map.of(), Map.of()));
            }
        } else {
            try {
                var encodedInputJapiMessage = serializer.deserializeFromMsgPack(inputJapiMessagePayload);
                if (encodedInputJapiMessage.size() < 3) {
                    return serializer.serializeToJson(List.of("error._ParseFailure", Map.of(), Map.of("reason", "JapiMessageArrayMustHaveThreeElements")));
                }
                inputJapiMessage = binaryEncoder.decode(encodedInputJapiMessage);
                inputIsBinary = true;
            } catch (BinaryEncoder.IncorrectBinaryHash e) {
                onError.accept(e);
                return serializer.serializeToJson(List.of("error._InvalidBinaryEncoding", Map.of(), Map.of()));
            } catch (Serializer.DeserializationError e) {
                onError.accept(e);
                return serializer.serializeToJson(List.of("error._ParseFailure", Map.of(), Map.of()));
            }
        }

        var outputJapiMessage = ProcessObject.process(inputJapiMessage, onError, binaryEncoder, apiDescription, internalHandler, handler);
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
    }}
