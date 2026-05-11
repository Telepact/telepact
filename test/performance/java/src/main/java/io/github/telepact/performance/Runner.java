//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

package io.github.telepact.performance;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.ArrayList;
import java.util.Base64;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.protobuf.DescriptorProtos.FileDescriptorSet;
import com.google.protobuf.Descriptors.Descriptor;
import com.google.protobuf.Descriptors.FieldDescriptor;
import com.google.protobuf.Descriptors.FileDescriptor;
import com.google.protobuf.DynamicMessage;

import io.github.telepact.Client;
import io.github.telepact.FunctionRoute;
import io.github.telepact.FunctionRouter;
import io.github.telepact.Message;
import io.github.telepact.Server;
import io.github.telepact.TelepactSchema;
import io.nats.client.Connection;
import io.nats.client.Dispatcher;
import io.nats.client.Nats;

public final class Runner {
    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();
    private static final TypeReference<Map<String, Object>> MAP_TYPE = new TypeReference<>() {};
    private static final TypeReference<Map<String, Map<String, Object>>> STRING_MAP_TYPE = new TypeReference<>() {};

    private record Args(
            String method,
            String collectionShape,
            String dataShape,
            String natsUrl,
            String subject,
            int iterations,
            int warmup,
            String payloads,
            String schemaDir) {
    }

    private static final class Sample {
        double requestSerializationMs;
        int requestSizeBytes;
        double requestNetworkTransitMs;
        double serverRequestDeserializationMs;
        double serverResponseSerializationMs;
        int responseSizeBytes;
        double responseNetworkTransitMs;
        double responseDeserializationMs;

        Map<String, Object> toMap() {
            return Map.of(
                    "request_serialization_ms", requestSerializationMs,
                    "request_size_bytes", requestSizeBytes,
                    "request_network_transit_ms", requestNetworkTransitMs,
                    "server_request_deserialization_ms", serverRequestDeserializationMs,
                    "server_response_serialization_ms", serverResponseSerializationMs,
                    "response_size_bytes", responseSizeBytes,
                    "response_network_transit_ms", responseNetworkTransitMs,
                    "response_deserialization_ms", responseDeserializationMs);
        }
    }

    private static final class PlainJsonCodec {
        byte[] encode(Map<String, Object> payload) {
            try {
                return OBJECT_MAPPER.writeValueAsBytes(payload);
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        }

        Map<String, Object> decode(byte[] payloadBytes) {
            try {
                return OBJECT_MAPPER.readValue(payloadBytes, MAP_TYPE);
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        }
    }

    private static final class ProtobufCodec {
        private final Descriptor requestDescriptor;
        private final Descriptor responseDescriptor;

        ProtobufCodec(Path schemaDir) throws Exception {
            final var descriptorPath = schemaDir.resolve("benchmark.desc.base64");
            final var descriptorBytes = Base64.getDecoder().decode(Files.readString(descriptorPath).trim());
            final var fileDescriptorSet = FileDescriptorSet.parseFrom(descriptorBytes);
            final var fileDescriptors = new HashMap<String, FileDescriptor>();
            for (var fileProto : fileDescriptorSet.getFileList()) {
                final var dependencies = new FileDescriptor[fileProto.getDependencyCount()];
                for (int i = 0; i < fileProto.getDependencyCount(); i += 1) {
                    dependencies[i] = fileDescriptors.get(fileProto.getDependency(i));
                }
                fileDescriptors.put(fileProto.getName(), FileDescriptor.buildFrom(fileProto, dependencies));
            }
            final var benchmark = fileDescriptors.get("benchmark.proto");
            if (benchmark == null) {
                throw new IllegalStateException("benchmark.proto descriptor missing");
            }
            this.requestDescriptor = benchmark.findMessageTypeByName("EchoRequest");
            this.responseDescriptor = benchmark.findMessageTypeByName("EchoResponse");
        }

        byte[] encodeRequest(Map<String, Object> payload) {
            return buildMessage(requestDescriptor, payload).toByteArray();
        }

        Map<String, Object> decodeRequest(byte[] bytes) throws Exception {
            return toPayload(DynamicMessage.parseFrom(requestDescriptor, bytes));
        }

        byte[] encodeResponse(Map<String, Object> payload) {
            return buildMessage(responseDescriptor, payload).toByteArray();
        }

        Map<String, Object> decodeResponse(byte[] bytes) throws Exception {
            return toPayload(DynamicMessage.parseFrom(responseDescriptor, bytes));
        }

        private DynamicMessage buildMessage(Descriptor descriptor, Map<String, Object> payload) {
            final var messageBuilder = DynamicMessage.newBuilder(descriptor);
            final var itemsField = descriptor.findFieldByName("items");
            @SuppressWarnings("unchecked")
            final var items = (List<Map<String, Object>>) payload.get("items");
            for (var item : items) {
                final var itemBuilder = DynamicMessage.newBuilder(itemsField.getMessageType());
                final var kind = (String) item.get("kind");
                @SuppressWarnings("unchecked")
                final var data = (Map<String, Object>) item.get("data");
                final var variantField = itemsField.getMessageType().findFieldByName(kind);
                final var variantBuilder = DynamicMessage.newBuilder(variantField.getMessageType());
                for (var field : variantField.getMessageType().getFields()) {
                    variantBuilder.setField(field, convertScalar(data.get(field.getName()), field));
                }
                itemBuilder.setField(variantField, variantBuilder.build());
                messageBuilder.addRepeatedField(itemsField, itemBuilder.build());
            }
            return messageBuilder.build();
        }

        private Map<String, Object> toPayload(DynamicMessage message) {
            final var result = new HashMap<String, Object>();
            final var items = new ArrayList<Map<String, Object>>();
            for (var rawItem : (List<?>) message.getField(message.getDescriptorForType().findFieldByName("items"))) {
                final var item = (DynamicMessage) rawItem;
                final var entry = new HashMap<String, Object>();
                final var oneOf = item.getDescriptorForType().getRealOneofs().getFirst();
                final var valueField = item.getOneofFieldDescriptor(oneOf);
                final var payload = new HashMap<String, Object>();
                if (valueField == null) {
                    throw new IllegalStateException("protobuf oneof missing");
                }
                final var valueMessage = (DynamicMessage) item.getField(valueField);
                for (var field : valueField.getMessageType().getFields()) {
                    payload.put(field.getName(), valueMessage.getField(field));
                }
                entry.put("kind", valueField.getName());
                entry.put("data", payload);
                items.add(entry);
            }
            result.put("items", items);
            return result;
        }

        private Object convertScalar(Object value, FieldDescriptor field) {
            return switch (field.getJavaType()) {
                case LONG, INT -> ((Number) value).longValue();
                case FLOAT, DOUBLE -> ((Number) value).doubleValue();
                case STRING -> String.valueOf(value);
                default -> value;
            };
        }
    }

    private static final class BenchmarkRunner {
        private final Args args;
        private final Map<String, Object> payload;
        private final Map<String, Object> responsePayload;
        private final TelepactSchema telepactSchema;
        private final ProtobufCodec protobufCodec;
        private final PlainJsonCodec plainJsonCodec = new PlainJsonCodec();
        private Connection connection;
        private Dispatcher dispatcher;
        private Sample currentSample;
        private double currentSendMs;
        private double serverReplySentMs;
        private double serverRequestHookMs;
        private double serverResponseHookMs;
        private boolean lastRequestWasBinary;
        private boolean lastResponseWasBinary;

        BenchmarkRunner(Args args) throws Exception {
            this.args = args;
            final var scenarios = OBJECT_MAPPER.readValue(Path.of(args.payloads).toFile(), STRING_MAP_TYPE);
            @SuppressWarnings("unchecked")
            final var payloadMap = (Map<String, Object>) scenarios.get(args.collectionShape).get(args.dataShape);
            this.payload = payloadMap;
            this.responsePayload = deepCopy(payloadMap);
            this.telepactSchema = TelepactSchema.fromDirectory(args.schemaDir);
            this.protobufCodec = new ProtobufCodec(Path.of(args.schemaDir));
        }

        void setup() throws Exception {
            this.connection = Nats.connect(args.natsUrl);
            startServer();
            connection.flush(Duration.ofSeconds(5));
        }

        void teardown() throws Exception {
            if (dispatcher != null) {
                dispatcher.unsubscribe(args.subject);
            }
            if (connection != null) {
                connection.close();
            }
        }

        Map<String, Object> run() throws Exception {
            int warmupIterations = args.warmup;
            if (args.method.equals("telepact-binary") || args.method.equals("telepact-packed-binary")) {
                warmupIterations = Math.max(warmupIterations, 1);
            }
            boolean steadyState = args.method.equals("telepact-json") || args.method.equals("protobuf")
                    || args.method.equals("plain-json");
            for (int i = 0; i < warmupIterations; i += 1) {
                steadyState |= runOnce().get("steady_state").equals(Boolean.TRUE);
            }
            while (!steadyState) {
                steadyState = (Boolean) runOnce().get("steady_state");
            }

            final var samples = new ArrayList<Map<String, Object>>();
            for (int i = 0; i < args.iterations; i += 1) {
                @SuppressWarnings("unchecked")
                final var runResult = (Map<String, Object>) runOnce().get("sample");
                samples.add(runResult);
            }
            return Map.of(
                    "language", "java",
                    "method", args.method,
                    "collection_shape", args.collectionShape,
                    "data_shape", args.dataShape,
                    "network_latency", args.natsUrl.contains("127.0.0.1") ? "close" : "far",
                    "warmup_iterations", warmupIterations,
                    "measured_iterations", args.iterations,
                    "samples", samples);
        }

        private Map<String, Object> runOnce() throws Exception {
            if (args.method.startsWith("telepact")) {
                return runTelepactOnce();
            }
            if (args.method.equals("protobuf")) {
                final var sample = runProtobufOnce();
                return Map.of("sample", sample.toMap(), "steady_state", true);
            }
            final var sample = runPlainJsonOnce();
            return Map.of("sample", sample.toMap(), "steady_state", true);
        }

        private void startServer() {
            if (args.method.startsWith("telepact")) {
                final var options = new Server.Options();
                options.authRequired = false;
                options.onRequest = (_message) -> this.serverRequestHookMs = nowMs();
                options.onResponse = (_message) -> this.serverResponseHookMs = nowMs();
                final FunctionRoute route = (_functionName, _message) -> new Message(Map.of(),
                        Map.of("Ok_", deepCopy(responsePayload)));
                final var server = new Server(telepactSchema, new FunctionRouter(Map.of("fn.echo", route)), options);
                this.dispatcher = connection.createDispatcher((io.nats.client.Message msg) -> {
                    try {
                        final var serverReceivedMs = nowMs();
                        final var response = server.process(msg.getData());
                        final var responseReadyMs = nowMs();
                        currentSample.requestNetworkTransitMs = serverReceivedMs - currentSendMs;
                        currentSample.serverRequestDeserializationMs = serverRequestHookMs - serverReceivedMs;
                        currentSample.serverResponseSerializationMs = responseReadyMs - serverResponseHookMs;
                        currentSample.responseSizeBytes = response.getBytes().length;
                        lastResponseWasBinary = response.getBytes()[0] == (byte) 0x92;
                        connection.publish(msg.getReplyTo(), response.getBytes());
                        serverReplySentMs = nowMs();
                    } catch (Exception e) {
                        throw new RuntimeException(e);
                    }
                });
                dispatcher.subscribe(args.subject);
                return;
            }
            if (args.method.equals("protobuf")) {
                this.dispatcher = connection.createDispatcher((io.nats.client.Message msg) -> {
                    try {
                        final var serverReceivedMs = nowMs();
                        final var decodeStartMs = nowMs();
                        final var decoded = protobufCodec.decodeRequest(msg.getData());
                        final var decodeEndMs = nowMs();
                        final var encodeStartMs = nowMs();
                        final var responseBytes = protobufCodec.encodeResponse(decoded);
                        final var encodeEndMs = nowMs();
                        currentSample.requestNetworkTransitMs = serverReceivedMs - currentSendMs;
                        currentSample.serverRequestDeserializationMs = decodeEndMs - decodeStartMs;
                        currentSample.serverResponseSerializationMs = encodeEndMs - encodeStartMs;
                        currentSample.responseSizeBytes = responseBytes.length;
                        connection.publish(msg.getReplyTo(), responseBytes);
                        serverReplySentMs = nowMs();
                    } catch (Exception e) {
                        throw new RuntimeException(e);
                    }
                });
                dispatcher.subscribe(args.subject);
                return;
            }
            this.dispatcher = connection.createDispatcher((io.nats.client.Message msg) -> {
                final var serverReceivedMs = nowMs();
                final var decodeStartMs = nowMs();
                final var decoded = plainJsonCodec.decode(msg.getData());
                final var decodeEndMs = nowMs();
                final var encodeStartMs = nowMs();
                final var responseBytes = plainJsonCodec.encode(decoded);
                final var encodeEndMs = nowMs();
                currentSample.requestNetworkTransitMs = serverReceivedMs - currentSendMs;
                currentSample.serverRequestDeserializationMs = decodeEndMs - decodeStartMs;
                currentSample.serverResponseSerializationMs = encodeEndMs - encodeStartMs;
                currentSample.responseSizeBytes = responseBytes.length;
                connection.publish(msg.getReplyTo(), responseBytes);
                serverReplySentMs = nowMs();
            });
            dispatcher.subscribe(args.subject);
        }

        private Map<String, Object> runTelepactOnce() {
            final var sample = new Sample();
            this.currentSample = sample;
            final var adapter = (Message requestMessage, io.github.telepact.Serializer serializer) -> {
                return java.util.concurrent.CompletableFuture.supplyAsync(() -> {
                    try {
                        final var serializeStartMs = nowMs();
                        final var requestBytes = serializer.serialize(requestMessage);
                        final var serializeEndMs = nowMs();
                        sample.requestSerializationMs = serializeEndMs - serializeStartMs;
                        sample.requestSizeBytes = requestBytes.length;
                        lastRequestWasBinary = requestBytes[0] == (byte) 0x92;
                        currentSendMs = nowMs();
                        final var responseMsg = connection.request(args.subject, requestBytes, Duration.ofSeconds(10));
                        if (responseMsg == null) {
                            throw new IllegalStateException("request timed out");
                        }
                        final var responseReceivedMs = nowMs();
                        sample.responseNetworkTransitMs = responseReceivedMs - serverReplySentMs;
                        final var deserializeStartMs = nowMs();
                        final var decoded = serializer.deserialize(responseMsg.getData());
                        final var deserializeEndMs = nowMs();
                        sample.responseDeserializationMs = deserializeEndMs - deserializeStartMs;
                        return decoded;
                    } catch (Exception e) {
                        throw new RuntimeException(e);
                    }
                });
            };
            final var options = new Client.Options();
            options.useBinary = !args.method.equals("telepact-json");
            options.alwaysSendJson = args.method.equals("telepact-json");
            final var client = new Client(adapter, options);
            final var headers = new HashMap<String, Object>();
            if (args.method.equals("telepact-packed-binary")) {
                headers.put("@pac_", true);
            }
            client.request(new Message(headers, Map.of("fn.echo", deepCopy(payload))));
            return Map.of(
                    "sample", sample.toMap(),
                    "steady_state", args.method.equals("telepact-json") || (lastRequestWasBinary && lastResponseWasBinary));
        }

        private Sample runProtobufOnce() throws Exception {
            final var sample = new Sample();
            this.currentSample = sample;
            final var serializeStartMs = nowMs();
            final var requestBytes = protobufCodec.encodeRequest(payload);
            final var serializeEndMs = nowMs();
            sample.requestSerializationMs = serializeEndMs - serializeStartMs;
            sample.requestSizeBytes = requestBytes.length;
            currentSendMs = nowMs();
            final var responseMsg = connection.request(args.subject, requestBytes, Duration.ofSeconds(10));
            if (responseMsg == null) {
                throw new IllegalStateException("request timed out");
            }
            final var responseReceivedMs = nowMs();
            sample.responseNetworkTransitMs = responseReceivedMs - serverReplySentMs;
            final var deserializeStartMs = nowMs();
            protobufCodec.decodeResponse(responseMsg.getData());
            final var deserializeEndMs = nowMs();
            sample.responseDeserializationMs = deserializeEndMs - deserializeStartMs;
            return sample;
        }

        private Sample runPlainJsonOnce() {
            final var sample = new Sample();
            this.currentSample = sample;
            final var serializeStartMs = nowMs();
            final var requestBytes = plainJsonCodec.encode(payload);
            final var serializeEndMs = nowMs();
            sample.requestSerializationMs = serializeEndMs - serializeStartMs;
            sample.requestSizeBytes = requestBytes.length;
            currentSendMs = nowMs();
            final var responseMsg = connection.request(args.subject, requestBytes, Duration.ofSeconds(10));
            if (responseMsg == null) {
                throw new IllegalStateException("request timed out");
            }
            final var responseReceivedMs = nowMs();
            sample.responseNetworkTransitMs = responseReceivedMs - serverReplySentMs;
            final var deserializeStartMs = nowMs();
            plainJsonCodec.decode(responseMsg.getData());
            final var deserializeEndMs = nowMs();
            sample.responseDeserializationMs = deserializeEndMs - deserializeStartMs;
            return sample;
        }
    }

    public static void main(String[] argv) throws Exception {
        final var runner = new BenchmarkRunner(parseArgs(argv));
        runner.setup();
        try {
            System.out.println(OBJECT_MAPPER.writeValueAsString(runner.run()));
        } finally {
            runner.teardown();
        }
    }

    private static Args parseArgs(String[] argv) {
        final var values = new HashMap<String, String>();
        for (int i = 0; i < argv.length; i += 2) {
            values.put(argv[i], argv[i + 1]);
        }
        return new Args(
                values.get("--method"),
                values.get("--collection-shape"),
                values.get("--data-shape"),
                values.get("--nats-url"),
                values.get("--subject"),
                Integer.parseInt(values.get("--iterations")),
                Integer.parseInt(values.get("--warmup")),
                values.get("--payloads"),
                values.get("--schema-dir"));
    }

    private static Map<String, Object> deepCopy(Map<String, Object> value) {
        return OBJECT_MAPPER.convertValue(value, MAP_TYPE);
    }

    private static double nowMs() {
        return System.nanoTime() / 1_000_000.0;
    }
}
