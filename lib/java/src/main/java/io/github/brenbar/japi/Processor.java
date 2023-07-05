package io.github.brenbar.japi;

import java.util.*;
import java.util.function.BiFunction;
import java.util.function.Consumer;
import java.util.function.Function;

public class Processor {

    interface Handler extends BiFunction<Context, Map<String, Object>, Map<String, Object>> {
    }

    interface ExtractContextProperties extends Function<Map<String, Object>, Map<String, Object>> {
    }

    interface Middleware extends BiFunction<List<Object>, Function<List<Object>, List<Object>>, List<Object>> {
    }

    Handler handler;
    Middleware middleware;
    ExtractContextProperties extractContextProperties;
    Map<String, Object> originalJApiAsParsedJson;
    Map<String, Definition> jApi;
    SerializationStrategy serializationStrategyx;
    Consumer<Throwable> onError;
    BinaryEncoder binaryEncoder;
    Serializer serializer;

    public Processor(String jApiAsJson, Handler handler) {
        var jApiTuple = InternalParse.newJApi(jApiAsJson);
        this.jApi = jApiTuple.parsed;
        this.originalJApiAsParsedJson = jApiTuple.original;

        var internalJApiTuple = InternalParse.newJApi(InternalJApi.JSON);

        this.jApi.putAll(internalJApiTuple.parsed);
        this.originalJApiAsParsedJson.putAll(internalJApiTuple.original);

        this.handler = handler;
        this.onError = (e) -> {
        };
        this.middleware = (i, n) -> n.apply(i);
        this.extractContextProperties = (h) -> new HashMap<>();

        this.binaryEncoder = InternalBinaryEncoderBuilder.build(jApi);

        this.serializer = new Serializer(new DefaultSerializationStrategy(),
                new ServerBinaryEncodingStrategy(binaryEncoder));
    }

    public Processor setOnError(Consumer<Throwable> onError) {
        this.onError = onError;
        return this;
    }

    public Processor setSerializationStrategy(SerializationStrategy strategy) {
        this.serializer.serializationStrategy = strategy;
        return this;
    }

    public Processor setExtractContextProperties(ExtractContextProperties extractContextProperties) {
        this.extractContextProperties = extractContextProperties;
        return this;
    }

    public byte[] process(byte[] inputMessageBytes) {
        return deserializeAndProcess(inputMessageBytes);
    }

    private byte[] deserializeAndProcess(byte[] inputMessageBytes) {
        try {
            List<Object> inputMessage;
            try {
                inputMessage = serializer.deserialize(inputMessageBytes);
            } catch (DeserializationError e) {
                var cause = e.getCause();
                if (cause instanceof BinaryEncoderUnavailableError e2) {
                    throw new JApiError("error._BinaryDecodeFailure", Map.of());
                } else {
                    throw new JApiError("error._ParseFailure", Map.of());
                }
            }

            var outputMessage = this.middleware.apply(inputMessage, this::processObject);

            return this.serializer.serialize(outputMessage);
        } catch (JApiError e) {
            this.onError.accept(e);
            return this.serializer.serialize(List.of(e.target, new HashMap<>(), e.body));
        } catch (Exception e) {
            this.onError.accept(e);
            return this.serializer.serialize(List.of("error._ProcessFailure", new HashMap<>(), Map.of()));
        }
    }

    private List<Object> processObject(List<Object> inputMessage) {
        return InternalProcess.processObject(inputMessage, this.onError, this.binaryEncoder, this.jApi,
                this.originalJApiAsParsedJson, this.handler, this.extractContextProperties);
    }
}
