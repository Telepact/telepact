package io.github.telepact;

import static io.github.telepact.internal.binary.ConstructBinaryEncoding.constructBinaryEncoding;

import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.protobuf.DescriptorProtos.FileDescriptorSet;
import com.google.protobuf.Descriptors.Descriptor;
import com.google.protobuf.Descriptors.FileDescriptor;
import com.google.protobuf.DynamicMessage;
import com.google.protobuf.util.JsonFormat;

import io.github.telepact.internal.binary.ServerBase64Encoder;
import io.github.telepact.internal.binary.ServerBinaryEncoder;
import io.nats.client.Connection;
import io.nats.client.Dispatcher;
import io.nats.client.Nats;
import io.nats.client.impl.NatsMessage;
import io.nats.client.impl.Headers;

public class PerformanceRunner {
    private static final Duration REQUEST_TIMEOUT = Duration.ofSeconds(30);
    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

    private record CaseDefinition(String dataShape, String collectionShape, String telepactFunction,
            String envelopeField, Map<String, Object> payload) {
    }

    private interface Codec {
        byte[] encodeRequest() throws Exception;

        void decodeRequest(byte[] bytes) throws Exception;

        byte[] encodeResponse() throws Exception;

        void decodeResponse(byte[] bytes) throws Exception;
    }

    private static final class PlainJsonCodec implements Codec {
        private final String envelopeField;
        private final Map<String, Object> requestObject;
        private final Map<String, Object> responseObject;

        private PlainJsonCodec(String envelopeField, Map<String, Object> payload) {
            this.envelopeField = envelopeField;
            this.requestObject = Map.of(envelopeField, payload);
            this.responseObject = Map.of(envelopeField, payload);
        }

        @Override
        public byte[] encodeRequest() throws Exception {
            return OBJECT_MAPPER.writeValueAsBytes(this.requestObject);
        }

        @Override
        public void decodeRequest(byte[] bytes) throws Exception {
            final var decoded = OBJECT_MAPPER.readValue(bytes, new TypeReference<Map<String, Object>>() {
            });
            if (!decoded.containsKey(this.envelopeField)) {
                throw new IllegalStateException("unexpected plain json request envelope");
            }
        }

        @Override
        public byte[] encodeResponse() throws Exception {
            return OBJECT_MAPPER.writeValueAsBytes(this.responseObject);
        }

        @Override
        public void decodeResponse(byte[] bytes) throws Exception {
            final var decoded = OBJECT_MAPPER.readValue(bytes, new TypeReference<Map<String, Object>>() {
            });
            if (!decoded.containsKey(this.envelopeField)) {
                throw new IllegalStateException("unexpected plain json response envelope");
            }
        }
    }

    private static final class ProtobufCodec implements Codec {
        private final String envelopeField;
        private final Descriptor requestDescriptor;
        private final Descriptor responseDescriptor;
        private final DynamicMessage requestMessage;
        private final DynamicMessage responseMessage;
        private final JsonFormat.Parser parser = JsonFormat.parser();

        private ProtobufCodec(Path descriptorSetPath, String envelopeField, Map<String, Object> payload) throws Exception {
            final var fileDescriptorSet = FileDescriptorSet.parseFrom(Files.readAllBytes(descriptorSetPath));
            final var descriptors = buildFileDescriptors(fileDescriptorSet);
            final var fileDescriptor = descriptors.get("performance.proto");
            this.requestDescriptor = fileDescriptor.findMessageTypeByName("Request");
            this.responseDescriptor = fileDescriptor.findMessageTypeByName("Response");
            this.envelopeField = envelopeField;
            this.requestMessage = parse(this.requestDescriptor, Map.of(envelopeField, payload));
            this.responseMessage = parse(this.responseDescriptor, Map.of(envelopeField, payload));
        }

        private DynamicMessage parse(Descriptor descriptor, Map<String, Object> payload) throws Exception {
            final var builder = DynamicMessage.newBuilder(descriptor);
            this.parser.merge(OBJECT_MAPPER.writeValueAsString(payload), builder);
            return builder.build();
        }

        @Override
        public byte[] encodeRequest() {
            return this.requestMessage.toByteArray();
        }

        @Override
        public void decodeRequest(byte[] bytes) throws Exception {
            final var message = DynamicMessage.parseFrom(this.requestDescriptor, bytes);
            if (message.getAllFields().keySet().stream().noneMatch(field -> field.getName().equals(this.envelopeField))) {
                throw new IllegalStateException("unexpected protobuf request envelope");
            }
        }

        @Override
        public byte[] encodeResponse() {
            return this.responseMessage.toByteArray();
        }

        @Override
        public void decodeResponse(byte[] bytes) throws Exception {
            final var message = DynamicMessage.parseFrom(this.responseDescriptor, bytes);
            if (message.getAllFields().keySet().stream().noneMatch(field -> field.getName().equals(this.envelopeField))) {
                throw new IllegalStateException("unexpected protobuf response envelope");
            }
        }
    }

    public static void main(String[] argv) throws Exception {
        final var args = parseArgs(argv);
        final var payloadJson = OBJECT_MAPPER.readValue(Path.of(args.get("payloads")).toFile(), new TypeReference<Map<String, Object>>() {
        });
        final var cases = loadCases(payloadJson);
        final var schema = TelepactSchema.fromDirectory(args.get("schema-dir"));
        final Connection clientConnection = Nats.connect(args.get("nats-url"));
        final Connection serverConnection = Nats.connect(args.get("nats-url"));
        try {
            final var results = new ArrayList<Map<String, Object>>();
            for (final var method : List.of("telepact_json", "telepact_binary", "telepact_packed_binary", "protobuf", "plain_json")) {
                for (final var caseDefinition : cases) {
                    results.add(executeCase(clientConnection, serverConnection, schema, caseDefinition, method,
                            Integer.parseInt(args.get("warmup")), Integer.parseInt(args.get("iterations")),
                            Path.of(args.get("descriptor-set"))));
                }
            }
            final var output = new LinkedHashMap<String, Object>();
            output.put("language", "java");
            output.put("natsUrl", args.get("nats-url"));
            output.put("warmupIterations", Integer.parseInt(args.get("warmup")));
            output.put("measuredIterations", Integer.parseInt(args.get("iterations")));
            output.put("cases", results);
            Files.writeString(Path.of(args.get("output")), OBJECT_MAPPER.writerWithDefaultPrettyPrinter().writeValueAsString(output) + "\n");
        } finally {
            clientConnection.close();
            serverConnection.close();
        }
    }

    private static Map<String, Object> executeCase(Connection clientConnection, Connection serverConnection,
            TelepactSchema schema, CaseDefinition caseDefinition, String method, int warmup, int iterations,
            Path descriptorSet) throws Exception {
        final var bench = method.startsWith("telepact_")
                ? buildTelepactCase(clientConnection, serverConnection, schema, caseDefinition, method)
                : buildNonTelepactCase(clientConnection, serverConnection, caseDefinition, method, descriptorSet);
        try {
            for (int i = 0; i < warmup; i++) {
                bench.run().call();
            }
            final var samples = new ArrayList<Map<String, Long>>();
            for (int i = 0; i < iterations; i++) {
                samples.add(bench.run().call());
            }
            final var result = new LinkedHashMap<String, Object>();
            result.put("method", method);
            result.put("dataShape", caseDefinition.dataShape());
            result.put("collectionShape", caseDefinition.collectionShape());
            result.put("samples", samples);
            return result;
        } finally {
            bench.finish().run();
        }
    }

    private record Bench(java.util.concurrent.Callable<Map<String, Long>> run, Runnable finish) {
    }

    private static Bench buildTelepactCase(Connection clientConnection, Connection serverConnection,
            TelepactSchema schema, CaseDefinition caseDefinition, String method) {
        final var subject = "telepact.performance.java." + java.util.UUID.randomUUID();
        final var serializer = new Serializer(new DefaultSerialization(), new ServerBinaryEncoder(constructBinaryEncoding(schema)),
                new ServerBase64Encoder());
        final Dispatcher dispatcher = serverConnection.createDispatcher((msg) -> {
            try {
                final long requestTransit = System.nanoTime() - Long.parseLong(msg.getHeaders().getFirst("x-client-sent-ns"));
                final long deserializeStart = System.nanoTime();
                final var requestMessage = serializer.deserialize(msg.getData());
                final long deserializeDuration = System.nanoTime() - deserializeStart;
                final var responseHeaders = new HashMap<String, Object>();
                if (requestMessage.headers.containsKey("@bin_")) {
                    responseHeaders.put("@binary_", true);
                    responseHeaders.put("@clientKnownBinaryChecksums_", requestMessage.headers.get("@bin_"));
                    if (requestMessage.headers.containsKey("@pac_")) {
                        responseHeaders.put("@pac_", requestMessage.headers.get("@pac_"));
                    }
                }
                final var responseMessage = new Message(responseHeaders, Map.of("Ok_", caseDefinition.payload()));
                final long serializeStart = System.nanoTime();
                final var responseBytes = serializer.serialize(responseMessage);
                final long serializeDuration = System.nanoTime() - serializeStart;
                final var headers = new Headers();
                headers.add("x-request-transit-ns", Long.toString(requestTransit));
                headers.add("x-server-request-deserialize-ns", Long.toString(deserializeDuration));
                headers.add("x-server-response-serialize-ns", Long.toString(serializeDuration));
                headers.add("x-server-sent-ns", Long.toString(System.nanoTime()));
                serverConnection.publish(NatsMessage.builder().subject(msg.getReplyTo()).headers(headers).data(responseBytes).build());
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        });
        dispatcher.subscribe(subject);
        try {
            serverConnection.flush(Duration.ofSeconds(5));
        } catch (Exception e) {
            throw new RuntimeException(e);
        }

        final var clientOptions = new Client.Options();
        clientOptions.useBinary = method.equals("telepact_binary") || method.equals("telepact_packed_binary");
        clientOptions.alwaysSendJson = method.equals("telepact_json");
        final var client = new Client((requestMessage, clientSerializer) -> java.util.concurrent.CompletableFuture.supplyAsync(() -> {
            try {
                final long serializeStart = System.nanoTime();
                final byte[] requestBytes = clientSerializer.serialize(requestMessage);
                final long clientRequestSerialize = System.nanoTime() - serializeStart;
                final var headers = new Headers();
                headers.add("x-client-sent-ns", Long.toString(System.nanoTime()));
                final var response = clientConnection.request(
                        NatsMessage.builder().subject(subject).headers(headers).data(requestBytes).build(), REQUEST_TIMEOUT);
                final long responseNetworkTransit = System.nanoTime() - Long.parseLong(response.getHeaders().getFirst("x-server-sent-ns"));
                final long deserializeStart = System.nanoTime();
                final var responseMessage = clientSerializer.deserialize(response.getData());
                final long clientResponseDeserialize = System.nanoTime() - deserializeStart;
                return new Message(
                        Map.of(
                                "clientRequestSerializeNs", clientRequestSerialize,
                                "requestSizeBytes", (long) requestBytes.length,
                                "requestNetworkTransitNs", Long.parseLong(response.getHeaders().getFirst("x-request-transit-ns")),
                                "serverRequestDeserializeNs", Long.parseLong(response.getHeaders().getFirst("x-server-request-deserialize-ns")),
                                "serverResponseSerializeNs", Long.parseLong(response.getHeaders().getFirst("x-server-response-serialize-ns")),
                                "responseSizeBytes", (long) response.getData().length,
                                "responseNetworkTransitNs", responseNetworkTransit,
                                "clientResponseDeserializeNs", clientResponseDeserialize),
                        responseMessage.body);
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        }), clientOptions);

        return new Bench(() -> {
            final var headers = new HashMap<String, Object>();
            if (method.equals("telepact_packed_binary")) {
                headers.put("@pac_", true);
            }
            final var response = client.request(new Message(headers, Map.of(caseDefinition.telepactFunction(), caseDefinition.payload())));
            if (!response.body.equals(Map.of("Ok_", caseDefinition.payload()))) {
                throw new IllegalStateException("unexpected telepact response");
            }
            final var sample = new LinkedHashMap<String, Long>();
            response.headers.forEach((key, value) -> sample.put(key, ((Number) value).longValue()));
            return sample;
        }, () -> dispatcher.unsubscribe(subject));
    }

    private static Bench buildNonTelepactCase(Connection clientConnection, Connection serverConnection,
            CaseDefinition caseDefinition, String method, Path descriptorSet) throws Exception {
        final var subject = "telepact.performance.java." + java.util.UUID.randomUUID();
        final Codec codec = method.equals("plain_json")
                ? new PlainJsonCodec(caseDefinition.envelopeField(), caseDefinition.payload())
                : new ProtobufCodec(descriptorSet, caseDefinition.envelopeField(), caseDefinition.payload());
        final Dispatcher dispatcher = serverConnection.createDispatcher((msg) -> {
            try {
                final long requestTransit = System.nanoTime() - Long.parseLong(msg.getHeaders().getFirst("x-client-sent-ns"));
                final long deserializeStart = System.nanoTime();
                codec.decodeRequest(msg.getData());
                final long deserializeDuration = System.nanoTime() - deserializeStart;
                final long serializeStart = System.nanoTime();
                final byte[] responseBytes = codec.encodeResponse();
                final long serializeDuration = System.nanoTime() - serializeStart;
                final var headers = new Headers();
                headers.add("x-request-transit-ns", Long.toString(requestTransit));
                headers.add("x-server-request-deserialize-ns", Long.toString(deserializeDuration));
                headers.add("x-server-response-serialize-ns", Long.toString(serializeDuration));
                headers.add("x-server-sent-ns", Long.toString(System.nanoTime()));
                serverConnection.publish(NatsMessage.builder().subject(msg.getReplyTo()).headers(headers).data(responseBytes).build());
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        });
        dispatcher.subscribe(subject);
        try {
            serverConnection.flush(Duration.ofSeconds(5));
        } catch (Exception e) {
            throw new RuntimeException(e);
        }

        return new Bench(() -> {
            final long serializeStart = System.nanoTime();
            final byte[] requestBytes = codec.encodeRequest();
            final long clientRequestSerialize = System.nanoTime() - serializeStart;
            final var headers = new Headers();
            headers.add("x-client-sent-ns", Long.toString(System.nanoTime()));
            final var response = clientConnection.request(
                    NatsMessage.builder().subject(subject).headers(headers).data(requestBytes).build(), REQUEST_TIMEOUT);
            final long responseNetworkTransit = System.nanoTime() - Long.parseLong(response.getHeaders().getFirst("x-server-sent-ns"));
            final long deserializeStart = System.nanoTime();
            codec.decodeResponse(response.getData());
            final long clientResponseDeserialize = System.nanoTime() - deserializeStart;
            final var sample = new LinkedHashMap<String, Long>();
            sample.put("clientRequestSerializeNs", clientRequestSerialize);
            sample.put("requestSizeBytes", (long) requestBytes.length);
            sample.put("requestNetworkTransitNs", Long.parseLong(response.getHeaders().getFirst("x-request-transit-ns")));
            sample.put("serverRequestDeserializeNs", Long.parseLong(response.getHeaders().getFirst("x-server-request-deserialize-ns")));
            sample.put("serverResponseSerializeNs", Long.parseLong(response.getHeaders().getFirst("x-server-response-serialize-ns")));
            sample.put("responseSizeBytes", (long) response.getData().length);
            sample.put("responseNetworkTransitNs", responseNetworkTransit);
            sample.put("clientResponseDeserializeNs", clientResponseDeserialize);
            return sample;
        }, () -> dispatcher.unsubscribe(subject));
    }

    private static List<CaseDefinition> loadCases(Map<String, Object> payloadJson) {
        final var cases = new ArrayList<CaseDefinition>();
        final var caseValues = (List<Map<String, Object>>) payloadJson.get("cases");
        for (final var caseValue : caseValues) {
            cases.add(new CaseDefinition(
                    (String) caseValue.get("dataShape"),
                    (String) caseValue.get("collectionShape"),
                    (String) caseValue.get("telepactFunction"),
                    (String) caseValue.get("envelopeField"),
                    (Map<String, Object>) caseValue.get("payload")));
        }
        return cases;
    }

    private static Map<String, String> parseArgs(String[] argv) {
        final var args = new HashMap<String, String>();
        for (int i = 0; i < argv.length; i += 2) {
            args.put(argv[i].replaceFirst("^--", ""), argv[i + 1]);
        }
        return args;
    }

    private static Map<String, FileDescriptor> buildFileDescriptors(FileDescriptorSet fileDescriptorSet) throws Exception {
        final var fileProtoByName = new HashMap<String, com.google.protobuf.DescriptorProtos.FileDescriptorProto>();
        for (final var file : fileDescriptorSet.getFileList()) {
            fileProtoByName.put(file.getName(), file);
        }
        final var descriptors = new HashMap<String, FileDescriptor>();
        for (final var file : fileDescriptorSet.getFileList()) {
            buildFileDescriptor(file.getName(), fileProtoByName, descriptors);
        }
        return descriptors;
    }

    private static FileDescriptor buildFileDescriptor(String name,
            Map<String, com.google.protobuf.DescriptorProtos.FileDescriptorProto> fileProtoByName,
            Map<String, FileDescriptor> descriptors) throws Exception {
        if (descriptors.containsKey(name)) {
            return descriptors.get(name);
        }
        final var fileProto = fileProtoByName.get(name);
        final var dependencies = new ArrayList<FileDescriptor>();
        for (final var dependencyName : fileProto.getDependencyList()) {
            dependencies.add(buildFileDescriptor(dependencyName, fileProtoByName, descriptors));
        }
        final var descriptor = FileDescriptor.buildFrom(fileProto, dependencies.toArray(FileDescriptor[]::new));
        descriptors.put(name, descriptor);
        return descriptor;
    }
}
