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
    JApiSchema jApiSchema;
    Consumer<Throwable> onError;
    BinaryEncoder binaryEncoder;
    Serializer serializer;

    public Processor(String jApiAsJson, Handler handler) {
        this.jApiSchema = InternalParse.newJApiSchemaWithInternalSchema(jApiAsJson);

        this.handler = handler;
        this.onError = (e) -> {
        };
        this.middleware = (i, n) -> n.apply(i);
        this.extractContextProperties = (h) -> new HashMap<>();

        this.binaryEncoder = InternalBinaryEncode.constructBinaryEncoder(this.jApiSchema);

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

    public byte[] process(byte[] requestMessageBytes) {
        return deserializeAndProcess(requestMessageBytes);
    }

    private byte[] deserializeAndProcess(byte[] requestMessageBytes) {
        try {
            try {
                var requestMessage = InternalProcess.reconstructRequestMessage(requestMessageBytes, this.serializer);

                var responseMessage = this.middleware.apply(requestMessage, this::processObject);

                return this.serializer.serialize(responseMessage);
            } catch (Exception e) {
                try {
                    this.onError.accept(e);
                } catch (Exception ignored) {
                }
                throw e;
            }
        } catch (InternalJApiError e) {
            return this.serializer.serialize(List.of(e.target, e.headers, e.body));
        } catch (Exception e) {
            return this.serializer.serialize(List.of("error._JApiFailure", new HashMap<>(), Map.of()));
        }
    }

    private List<Object> processObject(List<Object> requestMessage) {
        return InternalProcess.processObject(requestMessage, this.binaryEncoder,
                this.jApiSchema, this.handler, this.extractContextProperties);
    }
}
