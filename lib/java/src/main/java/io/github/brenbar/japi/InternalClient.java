package io.github.brenbar.japi;

import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.function.BiFunction;

class InternalClient {

    static FnMessage constructRequestMessage(Request request, boolean useBinaryDefault, boolean forceSendJsonDefault,
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

        return new FnMessage(headers, request.functionName, request.functionArgument);
    }

    static FnMessage processRequestObject(FnMessage request,
            BiFunction<Message, Serializer, Future<Message>> adapter, Serializer serializer, long timeoutMs) {
        try {
            var requestMessage = InternalMessage.convertFnMessage(request);
            var responseMessage = adapter.apply(requestMessage, serializer).get(timeoutMs, TimeUnit.MILLISECONDS);
            return InternalMessage.convertMessage(responseMessage);
        } catch (Exception e) {
            throw new ClientProcessError(e);
        }
    }
}
