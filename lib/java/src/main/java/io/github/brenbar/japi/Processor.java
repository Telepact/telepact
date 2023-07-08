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

    public byte[] process(byte[] inputMessageBytes) {
        return deserializeAndProcess(inputMessageBytes);
    }

    private byte[] deserializeAndProcess(byte[] inputMessageBytes) {
        try {
            var inputMessage = InternalProcess.reconstructRequestMessage(inputMessageBytes, this.serializer);

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
        return InternalProcess.processObject(inputMessage, this.onError, this.binaryEncoder,
                this.jApiSchema, this.handler, this.extractContextProperties);
    }
}
