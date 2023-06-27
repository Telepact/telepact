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

    private Handler handler;
    private Handler internalHandler;
    private Middleware middleware;
    private ExtractContextProperties extractContextProperties;
    private Map<String, Object> originalJApiAsParsedJson;
    private Map<String, Definition> jApi;
    private Serializer serializer;
    private Consumer<Throwable> onError;

    private BinaryEncoder binaryEncoder;

    public Processor(String jApiAsJson, Handler handler) {
        var jApiTuple = InternalParse.newJApi(jApiAsJson);
        this.jApi = jApiTuple.parsed();
        this.originalJApiAsParsedJson = jApiTuple.original();
        this.serializer = new DefaultSerializer();

        var internalJApiTuple = InternalParse.newJApi(InternalJApi.JSON);

        this.jApi.putAll(internalJApiTuple.parsed());
        this.originalJApiAsParsedJson.putAll(internalJApiTuple.original());

        this.handler = handler;
        this.internalHandler = InternalJApi.build(this.originalJApiAsParsedJson);
        this.onError = (e) -> {
        };
        this.middleware = (i, n) -> n.apply(i);
        this.extractContextProperties = (h) -> new HashMap<>();

        this.binaryEncoder = InternalBinaryEncoderBuilder.build(jApi);
    }

    public Processor setOnError(Consumer<Throwable> onError) {
        this.onError = onError;
        return this;
    }

    public Processor setSerializer(Serializer serializer) {
        this.serializer = serializer;
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
            List<Object> inputMessage = InternalProcess.deserialize(inputMessageBytes, this.serializer,
                    this.binaryEncoder);

            var outputMessage = this.middleware.apply(inputMessage, this::processObject);
            var outputHeaders = (Map<String, Object>) outputMessage.get(1);

            var returnAsBinary = outputHeaders.containsKey("_bin");

            boolean inputIsBinary = !InternalProcess.inputIsJson(inputMessageBytes);
            if (inputIsBinary || returnAsBinary) {
                var encodedOutputMessage = this.binaryEncoder.encode(outputMessage);
                return this.serializer.serializeToMsgPack(encodedOutputMessage);
            } else {
                return this.serializer.serializeToJson(outputMessage);
            }
        } catch (JApiError e) {
            this.onError.accept(e);
            return this.serializer.serializeToJson(List.of(e.target, Map.of(), e.body));
        } catch (Exception e) {
            this.onError.accept(e);
            return this.serializer.serializeToJson(List.of("error._ProcessFailure", Map.of(), Map.of()));
        }
    }

    private List<Object> processObject(List<Object> inputMessage) {
        return InternalProcess.processObject(inputMessage, this.onError, this.binaryEncoder, this.jApi,
                this.internalHandler, this.handler, this.extractContextProperties);
    }
}
