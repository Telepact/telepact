package io.github.brenbar.japi;

import java.nio.ByteBuffer;
import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;

import io.github.brenbar.japi.Client.Middleware;
import io.github.brenbar.japi.Client.ModifyHeaders;

public class AsyncClient {

    private static class Cache<K, V> extends LinkedHashMap<K, V> {

        private int maxSize;

        public Cache(int maxSize) {
            this.maxSize = maxSize;
        }

        @Override
        protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
            return this.size() > maxSize;
        }
    }

    private Client client;
    private Consumer<byte[]> asyncTransport;
    private Serializer serializer;
    private Long timeoutMs;

    public AsyncClient(Consumer<byte[]> asyncTransport) {
        this.client = new Client(this::serializeAndTransport);
        this.asyncTransport = asyncTransport;
        this.serializer = new DefaultSerializer();
        this.timeoutMs = 5000L;
    }

    public AsyncClient setSerializer(Serializer serializer) {
        this.serializer = serializer;
        return this;
    }

    public AsyncClient setTimeoutMs(Long timeoutMs) {
        this.timeoutMs = timeoutMs;
        return this;
    }

    public AsyncClient setModifyHeaders(ModifyHeaders modifyHeaders) {
        client.modifyHeaders = modifyHeaders;
        return this;
    }

    public AsyncClient setMiddleware(Middleware middleware) {
        client.middleware = middleware;
        return this;
    }

    public AsyncClient setUseBinary(boolean useBinary) {
        client.useBinary = useBinary;
        return this;
    }

    public AsyncClient setForceSendJson(boolean forceSendJson) {
        client.forceSendJson = forceSendJson;
        return this;
    }

    public Map<String, Object> call(
            Request jApiFunction) {
        return client.call(jApiFunction);
    }

    private static Map<Object, CompletableFuture<List<Object>>> waitingRequests = Collections
            .synchronizedMap(new Cache<Object, CompletableFuture<List<Object>>>(256));

    protected List<Object> serializeAndTransport(List<Object> inputJapiMessage, boolean sendAsMsgPack) {
        try {
            var id = generate32BitId();

            var headers = (Map<String, Object>) inputJapiMessage.get(1);
            headers.put("_id", id);
            headers.put("_tim", timeoutMs);

            var future = new CompletableFuture<List<Object>>();

            waitingRequests.put(id, future);

            byte[] inputJapiMessagePayload = InternalClientProcess.serialize(inputJapiMessage, serializer,
                    sendAsMsgPack);

            asyncTransport.accept(inputJapiMessagePayload);

            return future.get(timeoutMs, TimeUnit.MILLISECONDS);
        } catch (Exception e) {
            throw new ClientProcessError(e);
        }
    }

    public void receiveOutputJapiMessage(byte[] outputJapiMessagePayload) {
        try {
            List<Object> outputJapiMessage = InternalClientProcess.deserialize(outputJapiMessagePayload, serializer);

            var headers = (Map<String, Object>) outputJapiMessage.get(1);
            var id = headers.get("_id");

            waitingRequests.remove(id).complete(outputJapiMessage);
        } catch (Exception e) {
            throw new ClientProcessError(e);
        }

    }

    private String generate32BitId() {
        return Base64.getUrlEncoder().withoutPadding()
                .encodeToString(ByteBuffer.allocate(4).putInt(new Random().nextInt()).array());
    }
}
