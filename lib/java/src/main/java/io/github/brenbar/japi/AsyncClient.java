package io.github.brenbar.japi;

import java.nio.ByteBuffer;
import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeUnit;

public class AsyncClient extends Client {

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

    public interface AsyncTransport {
        void send(byte[] japiMessagePayload);
    }

    private AsyncTransport asyncTransport;
    private Serializer serializer;
    private Long timeoutMs;

    public AsyncClient(AsyncTransport asyncTransport) {
        this(asyncTransport, new Options());
    }

    public AsyncClient(AsyncTransport asyncTransport, Options options) {
        super(options);
        this.asyncTransport = asyncTransport;
        this.serializer = options.serializer;
        this.timeoutMs = options.timeoutMs;
    }

    private static Map<Object, CompletableFuture<List<Object>>> waitingRequests = Collections.synchronizedMap(new Cache<Object, CompletableFuture<List<Object>>>(256));

    @Override
    protected List<Object> serializeAndTransport(List<Object> inputJapiMessage, boolean useMsgPack) {
        try {
            var id = generate32BitId();

            var headers = (Map<String, Object>) inputJapiMessage.get(1);
            headers.put("_id", id);
            headers.put("_timeoutMs", timeoutMs);

            var future = new CompletableFuture<List<Object>>();

            waitingRequests.put(id, future);

            byte[] inputJapiMessagePayload;
            if (useMsgPack) {
                inputJapiMessagePayload = this.serializer.serializeToMsgPack(inputJapiMessage);
            } else {
                inputJapiMessagePayload = this.serializer.serializeToJson(inputJapiMessage);
            }

            asyncTransport.send(inputJapiMessagePayload);

            return future.get(timeoutMs, TimeUnit.MILLISECONDS);
        } catch (Exception e) {
            throw new ClientProcessError(e);
        }
    }

    public void receiveOutputJapiMessage(byte[] outputJapiMessagePayload) {
        try {
            List<Object> outputJapiMessage;
            if (outputJapiMessagePayload[0] == '[') {
                outputJapiMessage = serializer.deserializeFromJson(outputJapiMessagePayload);
            } else {
                outputJapiMessage = serializer.deserializeFromMsgPack(outputJapiMessagePayload);
            }

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
