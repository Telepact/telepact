package io.github.brenbar.japi;

import java.util.*;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.function.Function;

public class SyncClient extends Client {

    private Function<byte[], Future<byte[]>> syncTransport;
    private Serializer serializer;
    private Long timeoutMs;

    public SyncClient(Function<byte[], Future<byte[]>> syncTransport) {
        super();
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

    @Override
    protected List<Object> serializeAndTransport(List<Object> inputJapiMessage, boolean useMsgPack) {
        try {
            var headers = (Map<String, Object>) inputJapiMessage.get(1);
            headers.put("_tim", timeoutMs);

            byte[] inputJapiMessagePayload;
            if (useMsgPack) {
                inputJapiMessagePayload = this.serializer.serializeToMsgPack(inputJapiMessage);
            } else {
                inputJapiMessagePayload = this.serializer.serializeToJson(inputJapiMessage);
            }

            var outputJapiMessagePayload = syncTransport.apply(inputJapiMessagePayload).get(this.timeoutMs,
                    TimeUnit.MILLISECONDS);

            List<Object> outputJapiMessage;
            if (outputJapiMessagePayload[0] == '[') {
                outputJapiMessage = serializer.deserializeFromJson(outputJapiMessagePayload);
            } else {
                outputJapiMessage = serializer.deserializeFromMsgPack(outputJapiMessagePayload);
            }

            return outputJapiMessage;
        } catch (Exception e) {
            throw new ClientProcessError(e);
        }
    }
}
