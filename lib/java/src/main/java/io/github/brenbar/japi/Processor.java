package io.github.brenbar.japi;

import java.util.*;
import java.util.function.BiConsumer;
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
    private Map<String, Object> originalApiDescription;
    private Map<String, Definition> apiDescription;
    private Serializer serializer;
    private Consumer<Throwable> onError;

    private BinaryEncoder binaryEncoder;

    public Processor(Handler handler, String apiDescriptionJson) {
        var description = InternalParse.newJapi(apiDescriptionJson);
        this.apiDescription = description.parsed();
        this.originalApiDescription = description.original();
        this.serializer = new DefaultSerializer();

        var internalDescription = InternalParse.newJapi(InternalJapi.JSON);

        this.apiDescription.putAll(internalDescription.parsed());
        this.originalApiDescription.putAll(internalDescription.original());

        this.handler = handler;
        this.internalHandler = InternalJapi.build(this.originalApiDescription);
        this.onError = (e) -> {
        };
        this.middleware = (i, n) -> n.apply(i);
        this.extractContextProperties = (h) -> new HashMap<>();

        this.binaryEncoder = InternalBinaryEncoderBuilder.build(apiDescription);
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

    public byte[] process(byte[] inputJapiMessagePayload) {
        return deserializeAndProcess(inputJapiMessagePayload);
    }

    private byte[] deserializeAndProcess(byte[] inputJapiMessagePayload) {
        List<Object> inputJapiMessage;
        boolean inputIsBinary = false;
        if (inputJapiMessagePayload[0] == '[') {
            try {
                inputJapiMessage = this.serializer.deserializeFromJson(inputJapiMessagePayload);
            } catch (DeserializationError e) {
                // TODO: Need to swallow onError failures
                this.onError.accept(e);
                return this.serializer.serializeToJson(List.of("error._ParseFailure", Map.of(), Map.of()));
            }
        } else {
            try {
                var encodedInputJapiMessage = this.serializer.deserializeFromMsgPack(inputJapiMessagePayload);
                if (encodedInputJapiMessage.size() < 3) {
                    return this.serializer.serializeToJson(List.of("error._ParseFailure", Map.of(),
                            Map.of("reason", "JapiMessageArrayMustHaveThreeElements")));
                }
                inputJapiMessage = binaryEncoder.decode(encodedInputJapiMessage);
                inputIsBinary = true;
            } catch (IncorrectBinaryHashException e) {
                // TODO: Need to swallow onError failures
                this.onError.accept(e);
                return this.serializer.serializeToJson(List.of("error._InvalidBinaryEncoding", Map.of(), Map.of()));
            } catch (DeserializationError e) {
                // TODO: Need to swallow onError failures
                this.onError.accept(e);
                return this.serializer.serializeToJson(List.of("error._ParseFailure", Map.of(), Map.of()));
            }
        }

        var outputJapiMessage = this.middleware.apply(inputJapiMessage, this::processObject);
        var headers = (Map<String, Object>) outputJapiMessage.get(1);
        var returnAsBinary = headers.containsKey("_bin");
        if (!returnAsBinary && inputIsBinary) {
            headers.put("_bin", this.binaryEncoder.checksum);
        }

        if (inputIsBinary || returnAsBinary) {
            var encodedOutputJapiMessage = this.binaryEncoder.encode(outputJapiMessage);
            return this.serializer.serializeToMsgPack(encodedOutputJapiMessage);
        } else {
            return this.serializer.serializeToJson(outputJapiMessage);
        }
    }

    private List<Object> processObject(List<Object> jApiMessage) {
        return InternalProcess.processObject(jApiMessage, this.onError, this.binaryEncoder, this.apiDescription,
                this.internalHandler, this.handler, this.extractContextProperties);
    }
}
