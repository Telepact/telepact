package io.github.brenbar.japi;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicReference;
import java.util.stream.Collectors;

public abstract class Client {

    public static class Error extends RuntimeException {
        public final String type;
        public final Map<String, Object> body;

        public Error(String type, Map<String, Object> body) {
            super(type + ": " + body);
            this.type = type;
            this.body = body;
        }
    }

    public static class ClientProcessError extends RuntimeException {
        public ClientProcessError(Throwable cause) {
            super(cause);
        }
    }

    public interface Processor {
        List<Object> process(List<Object> japiMessage, Next next);
    }

    public interface Next {
        List<Object> proceed(List<Object> japiMessage);
    }

    private Processor processor;
    private boolean useBinary;
    private AtomicReference<BinaryEncoder> binaryEncoderStore = new AtomicReference<>();

    public static class Options {
        public Serializer serializer = new DefaultSerializer();
        public Processor processor = (m, n) -> n.proceed(m);
        public boolean useBinary = false;
        public long timeoutMs = 5000;

        public Options setSerializer(Serializer serializer) {
            this.serializer = serializer;
            return this;
        }

        public Options setProcessor(Processor processor) {
            this.processor = processor;
            return this;
        }

        public Options setUseBinary(boolean useBinary) {
            this.useBinary = useBinary;
            return this;
        }

        public Options setTimeoutMs(long timeoutMs) {
            this.timeoutMs = timeoutMs;
            return this;
        }
    }

    public Client(Options options) {
        this.processor = options.processor;
        this.useBinary = options.useBinary;
    }

    public Map<String, Object> call(
            String functionName,
            Map<String, Object> headers,
            Map<String, Object> input) {
        // Ensure our headers are editable.
        var mutableHeaders = new HashMap<>(headers);
        var messageType = "function.%s".formatted(functionName);
        var inputJapiMessage = List.of(messageType, mutableHeaders, input);
        var outputJapiMessage = this.processor.process(inputJapiMessage, this::proceed);

        var outputMessageType = (String) outputJapiMessage.get(0);
        var outputHeaders = (Map<String, Object>) outputJapiMessage.get(1);
        var output = (Map<String, Object>) outputJapiMessage.get(2);

        if (outputMessageType.startsWith("error.")) {
            throw new Error(outputMessageType, output);
        }

        return output;
    }

    private List<Object> proceed(List<Object> inputJapiMessage) {
        try {
            var headers = (Map<String, Object>) inputJapiMessage.get(1);
            var binaryEncoder = this.binaryEncoderStore.get();
            if (this.useBinary && binaryEncoder == null) {
                // Don't have schema yet. We'll have to send as JSON to start, and we'll ask the
                // jAPI provider to supply the binary encoding.
                headers.put("_binaryStart", true);
            }

            List<Object> outputJapiMessage;
            if (binaryEncoder != null) {
                headers.put("_bin", binaryEncoder.binaryHash);
                var encodedInputJapiMessage = binaryEncoder.encode(inputJapiMessage);
                var encodedOutputJapiMessage = serializeAndTransport(encodedInputJapiMessage, true);
                outputJapiMessage = binaryEncoder.decode(encodedOutputJapiMessage);
            } else {
                outputJapiMessage = serializeAndTransport(inputJapiMessage, false);
            }

            // If we received a binary encoding from the jAPI provider, cache it
            var outputHeaders = (Map<String, Object>) outputJapiMessage.get(1);
            if (outputHeaders.containsKey("_binaryEncoding")) {
                var binaryHash = (Object) outputHeaders.get("_bin");
                var initialBinaryEncoding = (Map<String, Object>) outputHeaders.get("_binaryEncoding");
                // Ensure everything is a long
                var binaryEncoding = initialBinaryEncoding.entrySet().stream()
                        .collect(Collectors.toMap(e -> e.getKey(), e -> {
                            var value = e.getValue();
                            if (value instanceof Integer i) {
                                return Long.valueOf(i);
                            } else if (value instanceof Long l) {
                                return l;
                            } else {
                                throw new RuntimeException("Unexpected type");
                            }
                        }));
                var newBinaryEncoder = new BinaryEncoder(binaryEncoding, binaryHash);
                this.binaryEncoderStore.set(newBinaryEncoder);

                return newBinaryEncoder.decode(outputJapiMessage);
            }

            return outputJapiMessage;
        } catch (Exception e) {
            throw new ClientProcessError(e);
        }
    }

    protected abstract List<Object> serializeAndTransport(List<Object> inputJapiMessage, boolean useMsgPack);

}
