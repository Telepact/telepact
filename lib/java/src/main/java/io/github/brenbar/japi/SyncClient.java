package io.github.brenbar.japi;

import java.util.*;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.function.Function;

import io.github.brenbar.japi.Client.Middleware;
import io.github.brenbar.japi.Client.ModifyHeaders;

public class SyncClient {

    private Client client;
    private Function<byte[], Future<byte[]>> syncTransport;
    private Serializer serializer;
    private Long timeoutMs;

    public SyncClient(Function<byte[], Future<byte[]>> syncTransport) {
        this.client = new Client(this::serializeAndTransport);
        this.syncTransport = syncTransport;
        this.serializer = new DefaultSerializer();
        this.timeoutMs = 5000L;
    }

    public SyncClient setSerializer(Serializer serializer) {
        this.serializer = serializer;
        return this;
    }

    public SyncClient setTimeoutMs(Long timeoutMs) {
        this.timeoutMs = timeoutMs;
        return this;
    }

    public SyncClient setModifyHeaders(ModifyHeaders modifyHeaders) {
        client.modifyHeaders = modifyHeaders;
        return this;
    }

    public SyncClient setMiddleware(Middleware middleware) {
        client.middleware = middleware;
        return this;
    }

    public SyncClient setUseBinary(boolean useBinary) {
        client.useBinary = useBinary;
        return this;
    }

    public SyncClient setForceSendJson(boolean forceSendJson) {
        client.forceSendJson = forceSendJson;
        return this;
    }

    public Map<String, Object> submit(
            Request request) {
        return client.submit(request);
    }

    protected List<Object> serializeAndTransport(List<Object> inputMessage, boolean sendAsMsgPack) {
        try {
            var headers = (Map<String, Object>) inputMessage.get(1);
            headers.put("_tim", timeoutMs);

            byte[] inputMessageBytes = InternalClientProcess.serialize(inputMessage, serializer,
                    sendAsMsgPack);

            var outputMessageBytes = syncTransport.apply(inputMessageBytes).get(this.timeoutMs,
                    TimeUnit.MILLISECONDS);

            List<Object> outputMessage = InternalClientProcess.deserialize(outputMessageBytes, serializer);
            return outputMessage;
        } catch (Exception e) {
            throw new ClientProcessError(e);
        }
    }
}
