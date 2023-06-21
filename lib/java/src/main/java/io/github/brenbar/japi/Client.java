package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.Deque;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.ConcurrentLinkedDeque;
import java.util.stream.Collectors;

public abstract class Client {

    private ClientProcessor processor;
    private boolean useBinary;
    private boolean forceSendJson;
    private Deque<BinaryEncoder> binaryEncoderStore = new ConcurrentLinkedDeque<>();

    public Client(ClientOptions options) {
        this.processor = options.processor;
        this.useBinary = options.useBinary;
        this.forceSendJson = options.forceSendJson;
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
            throw new ClientError(outputMessageType, output);
        }

        return output;
    }

    private List<Object> proceed(List<Object> inputJapiMessage) {
        try {
            var headers = (Map<String, Object>) inputJapiMessage.get(1);

            if (this.useBinary) {
                List<Object> binaryChecksums = new ArrayList<>();
                for (var binaryEncoding : binaryEncoderStore) {
                    binaryChecksums.add(binaryEncoding.checksum);
                }
                headers.put("_bin", binaryChecksums);
            }

            var binaryEncoder = this.binaryEncoderStore.size() == 0 ? null : this.binaryEncoderStore.getFirst();
            List<Object> finalInputJapiMessage;
            boolean sendAsMsgPack = false;
            if (this.forceSendJson || !this.useBinary || binaryEncoder == null) {
                finalInputJapiMessage = inputJapiMessage;
            } else {
                finalInputJapiMessage = binaryEncoder.encode(inputJapiMessage);
                sendAsMsgPack = true;
            }

            var outputJapiMessage = serializeAndTransport(finalInputJapiMessage, sendAsMsgPack);
            var outputHeaders = (Map<String, Object>) outputJapiMessage.get(1);

            // If the response is in binary, decode it
            if (outputHeaders.containsKey("_bin")) {
                var binaryChecksum = (List<Long>) outputHeaders.get("_bin");

                if (outputHeaders.containsKey("_binaryEncoding")) {
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
                    var newBinaryEncoder = new BinaryEncoder(binaryEncoding, binaryChecksum.get(0));
                    this.binaryEncoderStore.add(newBinaryEncoder);

                    // We need to maintain 2 binary encodings in case a server is undergoing an API
                    // change during a new jAPI deployment
                    if (this.binaryEncoderStore.size() >= 3) {
                        this.binaryEncoderStore.removeLast();
                    }
                }

                var outputBinaryEncoder = findBinaryEncoder(binaryChecksum.get(0));

                return outputBinaryEncoder.decode(outputJapiMessage);
            }

            return outputJapiMessage;
        } catch (Exception e) {
            throw new ClientProcessError(e);
        }
    }

    private BinaryEncoder findBinaryEncoder(Long checksum) {
        for (var binaryEncoder : this.binaryEncoderStore) {
            if (Objects.equals(binaryEncoder.checksum, checksum)) {
                return binaryEncoder;
            }
        }
        throw new ClientProcessError(new Exception("No matching encoding found, cannot decode binary"));
    }

    protected abstract List<Object> serializeAndTransport(List<Object> inputJapiMessage, boolean useMsgPack);

}
