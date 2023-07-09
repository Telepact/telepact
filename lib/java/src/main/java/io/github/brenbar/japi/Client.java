package io.github.brenbar.japi;

import java.util.List;
import java.util.Map;
import java.util.concurrent.Future;
import java.util.function.BiFunction;
import java.util.function.Function;

public class Client {

    interface Middleware extends BiFunction<List<Object>, Function<List<Object>, List<Object>>, List<Object>> {
    }

    interface Adapter extends BiFunction<List<Object>, Serializer, Future<List<Object>>> {
    }

    private Adapter adapter;
    private Serializer serializer;
    private Middleware middleware;
    boolean useBinaryDefault;
    boolean forceSendJsonDefault;
    long timeoutMsDefault;

    public Client(Adapter adapter) {
        this.adapter = adapter;

        this.middleware = (m, n) -> n.apply(m);
        this.useBinaryDefault = false;
        this.forceSendJsonDefault = true;
        this.timeoutMsDefault = 5000;

        this.serializer = new Serializer(new DefaultSerializationStrategy(),
                new InternalClientBinaryEncodingStrategy());
    }

    public Client setMiddleware(Middleware middleware) {
        this.middleware = middleware;
        return this;
    }

    public Client setUseBinaryDefault(boolean useBinary) {
        this.useBinaryDefault = useBinary;
        return this;
    }

    public Client setForceSendJsonDefault(boolean forceSendJson) {
        this.forceSendJsonDefault = forceSendJson;
        return this;
    }

    public Client setTimeoutMsDefault(long timeoutMs) {
        this.timeoutMsDefault = timeoutMs;
        return this;
    }

    public Client setSerializationStrategy(SerializationStrategy serializationStrategy) {
        this.serializer.serializationStrategy = serializationStrategy;
        return this;
    }

    public Map<String, Object> submit(
            Request request) {

        var requestMessage = InternalClientProcess.constructRequestMessage(request, useBinaryDefault,
                forceSendJsonDefault, timeoutMsDefault);

        var outputJapiMessage = this.middleware.apply(requestMessage, this::processMessage);

        var outputMessageType = (String) outputJapiMessage.get(0);
        var output = (Map<String, Object>) outputJapiMessage.get(2);

        if (outputMessageType.startsWith("error.")) {
            throw new JApiError(outputMessageType, output);
        }

        return output;
    }

    public List<Object> processMessage(List<Object> message) {
        return InternalClientProcess.processRequestObject(message, this.adapter, this.serializer,
                this.timeoutMsDefault);
    }

}
