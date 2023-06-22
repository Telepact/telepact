package io.github.brenbar.japi;

import java.util.*;
import java.util.function.BiConsumer;
import java.util.function.BiFunction;
import java.util.function.Consumer;

public class Processor {

    static class ServerContext {
        public final String functionName;
        public final Map<String, Object> properties = new HashMap<String, Object>();

        public ServerContext(String functionName) {
            this.functionName = functionName;
        }
    }

    interface PreProcess extends BiConsumer<ServerContext, Map<String, Object>> {
    }

    interface Handler extends BiFunction<ServerContext, Map<String, Object>, Map<String, Object>> {
    }

    private Handler handler;
    private Handler internalHandler;
    private Map<String, Object> originalApiDescription;
    private Map<String, Definition> apiDescription;
    private Serializer serializer;
    private Consumer<Throwable> onError;

    private BinaryEncoder binaryEncoder;

    public static class Options {
        private Consumer<Throwable> onError = (e) -> {
        };
        private Serializer serializer = new DefaultSerializer();

        public Options setOnError(Consumer<Throwable> onError) {
            this.onError = onError;
            return this;
        }

        public Options setSerializer(Serializer serializer) {
            this.serializer = serializer;
            return this;
        }
    }

    public Processor(Handler handler, String apiDescriptionJson) {
        this(handler, apiDescriptionJson, new Options());
    }

    public Processor(Handler handler, String apiDescriptionJson, Options options) {
        var description = InternalParse.newJapi(apiDescriptionJson);
        this.apiDescription = description.parsed();
        this.originalApiDescription = description.original();
        this.serializer = options.serializer;

        var internalDescription = InternalParse.newJapi(InternalJapi.JSON);

        this.apiDescription.putAll(internalDescription.parsed());
        this.originalApiDescription.putAll(internalDescription.original());

        this.handler = handler;
        this.internalHandler = InternalJapi.build(this.originalApiDescription);
        this.onError = options.onError;

        this.binaryEncoder = InternalBinaryEncoderBuilder.build(apiDescription);
    }

    public byte[] process(byte[] inputJapiMessagePayload) {
        return InternalProcess.process(inputJapiMessagePayload, serializer, onError, binaryEncoder, apiDescription,
                internalHandler, handler);
    }
}
