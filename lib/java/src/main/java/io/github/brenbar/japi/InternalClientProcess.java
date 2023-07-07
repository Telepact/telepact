package io.github.brenbar.japi;

import java.util.List;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.function.BiFunction;

class InternalClientProcess {

    static List<Object> constructRequestMessage(Request request, boolean useBinaryDefault, boolean forceSendJsonDefault,
            long timeoutMsDefault) {
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

        long finalTimeoutMs;
        if (request.timeoutMs.isPresent()) {
            finalTimeoutMs = request.timeoutMs.get();
        } else {
            finalTimeoutMs = timeoutMsDefault;
        }

        var headers = request.headers;

        if (!request.selectedStructFields.isEmpty()) {
            headers.put("_sel", request.selectedStructFields);
        }

        if (finalForceSendJson) {
            headers.put("_serializeAsJson", finalForceSendJson);
        }

        headers.put("_tim", finalTimeoutMs);

        if (finalUseBinary) {
            headers.put("_serializeAsBinary", true);
        }

        var messageType = "function.%s".formatted(request.functionName);
        return List.of(messageType, headers, request.functionInput);
    }

    static List<Object> processRequestObject(List<Object> inputJapiMessage,
            BiFunction<List<Object>, Serializer, Future<List<Object>>> adapter, Serializer serializer, long timeoutMs) {
        try {
            return adapter.apply(inputJapiMessage, serializer).get(timeoutMs, TimeUnit.MILLISECONDS);
        } catch (Exception e) {
            throw new ClientProcessError(e);
        }
    }
}
