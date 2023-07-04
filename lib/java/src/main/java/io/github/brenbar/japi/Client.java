package io.github.brenbar.japi;

import java.util.Deque;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentLinkedDeque;
import java.util.concurrent.Future;
import java.util.function.BiFunction;
import java.util.function.Function;

class Client {

    interface SerializeAndTransport extends BiFunction<List<Object>, Boolean, Future<List<Object>>> {
    }

    interface ModifyHeaders extends Function<Map<String, Object>, Map<String, Object>> {
    }

    interface Middleware extends BiFunction<List<Object>, Function<List<Object>, List<Object>>, List<Object>> {
    }

    private SerializeAndTransport serializeAndTransport;
    ModifyHeaders modifyHeaders;
    Middleware middleware;
    private Deque<BinaryEncoder> recentBinaryEncoders = new ConcurrentLinkedDeque<>();
    boolean useBinaryDefault;
    boolean forceSendJsonDefault;
    long timeoutMsDefault;

    public Client(SerializeAndTransport serializeAndTransport) {
        this.serializeAndTransport = serializeAndTransport;
        this.modifyHeaders = (h) -> h;
        this.middleware = (m, n) -> n.apply(m);
        this.useBinaryDefault = false;
        this.forceSendJsonDefault = true;
        this.timeoutMsDefault = timeoutMsDefault;
    }

    public Client setModifyHeaders(ModifyHeaders modifyHeaders) {
        this.modifyHeaders = modifyHeaders;
        return this;
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

    public Map<String, Object> submit(
            Request request) {
        return InternalClientProcess.submit(request, this.serializeAndTransport, this.modifyHeaders, this.middleware,
                this.recentBinaryEncoders, this.useBinaryDefault,
                this.forceSendJsonDefault, this.timeoutMsDefault);
    }

}
