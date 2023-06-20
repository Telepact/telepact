package io.github.brenbar.japi;

public class ClientOptions {
    public Serializer serializer = new DefaultSerializer();
    public ClientProcessor processor = (m, n) -> n.proceed(m);
    public boolean useBinary = false;
    public boolean forceSendJson = true;
    public long timeoutMs = 5000;

    public ClientOptions setSerializer(Serializer serializer) {
        this.serializer = serializer;
        return this;
    }

    public ClientOptions setProcessor(ClientProcessor processor) {
        this.processor = processor;
        return this;
    }

    public ClientOptions setUseBinary(boolean useBinary) {
        this.useBinary = useBinary;
        return this;
    }

    public ClientOptions setForceSendJson(boolean sendBinary) {
        this.forceSendJson = sendBinary;
        return this;
    }

    public ClientOptions setTimeoutMs(long timeoutMs) {
        this.timeoutMs = timeoutMs;
        return this;
    }
}