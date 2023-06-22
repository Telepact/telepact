package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.Deque;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.ConcurrentLinkedDeque;
import java.util.function.BiConsumer;
import java.util.function.BiFunction;
import java.util.function.Function;
import java.util.stream.Collectors;

public abstract class Client {

    private Client.PreProcess preProcess;
    private boolean useBinary;
    private boolean forceSendJson;
    private Deque<BinaryEncoder> binaryEncoderStore = new ConcurrentLinkedDeque<>();

    interface Process extends Function<List<Object>, List<Object>> {
    }

    interface PreProcess extends Function<JApiFunction, JApiFunction> {
    }

    public Client() {
        this.preProcess = (f) -> f;
        this.useBinary = false;
        this.forceSendJson = true;
    }

    public Client setPreProcess(Client.PreProcess preProcess) {
        this.preProcess = preProcess;
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
            JApiFunction jApiFunction) {
        return InternalClientProcess.call(jApiFunction, this.preProcess);
    }

    protected abstract List<Object> serializeAndTransport(List<Object> inputJapiMessage, boolean useMsgPack);

}
