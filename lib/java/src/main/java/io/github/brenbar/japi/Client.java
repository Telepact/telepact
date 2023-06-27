package io.github.brenbar.japi;

import java.util.Deque;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentLinkedDeque;
import java.util.function.BiFunction;
import java.util.function.Function;

class Client {

    interface SerializeAndTransport extends BiFunction<List<Object>, Boolean, List<Object>> {
    }

    interface ModifyHeaders extends Function<Map<String, Object>, Map<String, Object>> {
    }

    interface Middleware extends BiFunction<List<Object>, Function<List<Object>, List<Object>>, List<Object>> {
    }

    private SerializeAndTransport serializeAndTransport;
    ModifyHeaders modifyHeaders;
    Middleware middleware;
    private Deque<BinaryEncoder> recentBinaryEncoders = new ConcurrentLinkedDeque<>();
    boolean useBinary;
    boolean forceSendJson;

    public Client(SerializeAndTransport serializeAndTransport) {
        this.serializeAndTransport = serializeAndTransport;
        this.modifyHeaders = (h) -> h;
        this.middleware = (m, n) -> n.apply(m);
        this.useBinary = false;
        this.forceSendJson = true;
    }

    public Client setModifyHeaders(ModifyHeaders modifyHeaders) {
        this.modifyHeaders = modifyHeaders;
        return this;
    }

    public Client setMiddleware(Middleware middleware) {
        this.middleware = middleware;
        return this;
    }

    public Client setUseBinary(boolean useBinary) {
        this.useBinary = useBinary;
        return this;
    }

    public Client setForceSendJson(boolean forceSendJson) {
        this.forceSendJson = forceSendJson;
        return this;
    }

    public Map<String, Object> call(
            Request jApiFunction) {
        return InternalClientProcess.call(jApiFunction, this.serializeAndTransport, this.modifyHeaders, this.middleware,
                this.recentBinaryEncoders, this.useBinary,
                this.forceSendJson);
    }

}
