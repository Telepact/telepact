package io.github.brenbar.japi;

import java.util.*;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;

public class SyncClient extends Client {

    public interface SyncTransport {
        Future<byte[]> send(byte[] japiMessagePayload);
    }

    private SyncTransport syncTransport;
    private Serializer serializer;
    private Long timeoutMs;

    public SyncClient(SyncTransport syncTransport) {
        this(syncTransport, new ClientOptions());
    }

    public SyncClient(SyncTransport syncTransport, ClientOptions options) {
        super(options);
        this.syncTransport = syncTransport;
        this.serializer = options.serializer;
        this.timeoutMs = options.timeoutMs;
    }

    @Override
    protected List<Object> serializeAndTransport(List<Object> inputJapiMessage, boolean useMsgPack) {
        try {
            byte[] inputJapiMessagePayload;
            if (useMsgPack) {
                inputJapiMessagePayload = this.serializer.serializeToMsgPack(inputJapiMessage);
            } else {
                inputJapiMessagePayload = this.serializer.serializeToJson(inputJapiMessage);
            }

            var outputJapiMessagePayload = syncTransport.send(inputJapiMessagePayload).get(timeoutMs,
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
