package io.github.brenbar.japi.server;

import io.github.brenbar.japi.BinaryEncoder;
import io.github.brenbar.japi.DefaultSerializer;
import io.github.brenbar.japi.Serializer;

import java.util.*;
import java.util.function.Consumer;

public class Processor {

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
        var description = Parser.newJapi(apiDescriptionJson);
        this.apiDescription = description.parsed();
        this.originalApiDescription = description.original();
        this.serializer = options.serializer;

        var internalDescription = Parser.newJapi(InternalJapi.JSON);

        this.apiDescription.putAll(internalDescription.parsed());
        this.originalApiDescription.putAll(internalDescription.original());

        this.handler = handler;
        this.internalHandler = InternalJapi.build(this.originalApiDescription);
        this.onError = options.onError;

        this.binaryEncoder = BuildBinaryEncoder.build(apiDescription);
    }

    public byte[] process(byte[] inputJapiMessagePayload) {
        return ProcessBytes.process(inputJapiMessagePayload, serializer, onError, binaryEncoder, apiDescription,
                internalHandler, handler);
    }
}
