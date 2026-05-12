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

package telepact.performance;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.protobuf.DescriptorProtos;
import com.google.protobuf.Descriptors;
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
import io.nats.client.Options;
import java.io.File;
import java.nio.file.Path;
import java.time.Duration;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Future;
import java.util.function.BiFunction;

public class Main {
    private static final List<String> NETWORKS = List.of("close", "far");
    private static final List<String> DATA_SHAPES = List.of("typical", "all-strings", "all-numbers");
    private static final List<String> COLLECTION_SHAPES = List.of("single", "small-list", "big-list", "really-big-list", "huge-list");
    private static final List<String> METHODS = List.of("telepact-json", "telepact-binary", "telepact-packed-binary", "protobuf", "plain-json");
    private static final Map<String, String> FUNCTION_NAMES = Map.of(
            "typical", "fn.roundTripTypical",
            "all-strings", "fn.roundTripStrings",
            "all-numbers", "fn.roundTripNumbers");
    private static final Map<String, String> PLAIN_FUNCTION_NAMES = Map.of(
            "typical", "roundTripTypical",
            "all-strings", "roundTripStrings",
            "all-numbers", "roundTripNumbers");
    private static final Duration NATS_TIMEOUT = Duration.ofSeconds(15);
    private static final int NATS_REQUEST_ADDITIONAL_RETRIES = 2;
    private static final Duration NATS_RETRY_DELAY = Duration.ofMillis(250);
    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();
    private static final Map<String, ProtobufTypes> PROTO_TYPES = createProtobufTypes();

    record Scenario(String networkLatency, String dataShape, String collectionShape, String method) {}
    record ServerMetrics(long requestNetworkArrivalNs, long serverRequestDeserializationTimeNs, long serverResponseSerializationTimeNs, long responseSentAtNs) {}
    record ProtobufTypes(
            Descriptors.Descriptor requestDescriptor,
            Descriptors.FieldDescriptor requestItemsField,
            Descriptors.Descriptor responseDescriptor,
            Descriptors.FieldDescriptor responseItemsField,
            Descriptors.Descriptor itemDescriptor) {}

    public static void main(String[] args) throws Exception {
        var parsed = parseArgs(args);
        var iterations = Integer.parseInt(parsed.get("iterations"));
        var warmupIterations = Integer.parseInt(parsed.get("warmup-iterations"));
        var localNatsUrl = parsed.get("local-nats-url");
        var remoteNatsUrl = parsed.get("remote-nats-url");
        var output = parsed.get("output");
        var payloads = loadPayloads();
        var scenarios = new ArrayList<Object>();

        for (var networkLatency : NETWORKS) {
            var natsUrl = Objects.equals(networkLatency, "close") ? localNatsUrl : remoteNatsUrl;
            var options = new Options.Builder().server(natsUrl).build();
            try (var clientConnection = Nats.connect(options); var serverConnection = Nats.connect(options)) {
                for (var dataShape : DATA_SHAPES) {
                    for (var collectionShape : COLLECTION_SHAPES) {
                        for (var method : METHODS) {
                            var scenario = new Scenario(networkLatency, dataShape, collectionShape, method);
                            var payload = (List<Map<String, Object>>) ((Map<String, Object>) payloads.get(dataShape)).get(collectionShape);
                            var queue = new ArrayBlockingQueue<ServerMetrics>(1);
                            var subject = "perf.java." + UUID.randomUUID();
                            var runner = createRunner(serverConnection, clientConnection, subject, scenario, queue);
                            try {
                                for (int i = 0; i < warmupIterations; i += 1) {
                                    runner.requestOnce(payload);
                                }
                                var samples = new ArrayList<Object>();
                                for (int i = 0; i < iterations; i += 1) {
                                    samples.add(runner.requestOnce(payload));
                                }
                                scenarios.add(Map.of(
                                        "language", "java",
                                        "networkLatency", networkLatency,
                                        "dataShape", dataShape,
                                        "collectionShape", collectionShape,
                                        "method", method,
                                        "iterations", iterations,
                                        "warmupIterations", warmupIterations,
                                        "samples", samples));
                            } finally {
                                runner.close();
                            }
                        }
                    }
                }
            }
        }

        OBJECT_MAPPER.writeValue(new File(output), Map.of(
                "metadata", Map.of(
                        "language", "java",
                        "generatedAt", java.time.OffsetDateTime.now().toString(),
                        "iterations", iterations,
                        "warmupIterations", warmupIterations,
                        "localNatsUrl", localNatsUrl,
                        "remoteNatsUrl", remoteNatsUrl),
                "scenarios", scenarios));
    }

    private static Runner createRunner(Connection serverConnection, Connection clientConnection, String subject, Scenario scenario, ArrayBlockingQueue<ServerMetrics> queue) throws Exception {
        return switch (scenario.method()) {
            case "plain-json" -> createPlainJsonRunner(serverConnection, clientConnection, subject, scenario, queue);
            case "protobuf" -> createProtobufRunner(serverConnection, clientConnection, subject, scenario, queue);
            default -> createTelepactRunner(serverConnection, clientConnection, subject, scenario, queue);
        };
    }

    private static Runner createPlainJsonRunner(Connection serverConnection, Connection clientConnection, String subject, Scenario scenario, ArrayBlockingQueue<ServerMetrics> queue) {
        var dispatcher = serverConnection.createDispatcher(msg -> {
            try {
                long receivedAt = System.nanoTime();
                var request = OBJECT_MAPPER.readValue(msg.getData(), new TypeReference<Map<String, Object>>() {});
                long afterDeserialize = System.nanoTime();
                var response = Map.of("function", request.get("function"), "items", request.get("items"));
                long beforeSerialize = System.nanoTime();
                var responseBytes = OBJECT_MAPPER.writeValueAsBytes(response);
                long responseSentAt = System.nanoTime();
                queue.put(new ServerMetrics(receivedAt, afterDeserialize - receivedAt, responseSentAt - beforeSerialize, responseSentAt));
                serverConnection.publish(msg.getReplyTo(), responseBytes);
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        });
        dispatcher.subscribe(subject);
        return new Runner(dispatcher, payload -> {
            var request = Map.of("function", PLAIN_FUNCTION_NAMES.get(scenario.dataShape()), "items", payload);
            long serializeStart = System.nanoTime();
            var requestBytes = OBJECT_MAPPER.writeValueAsBytes(request);
            long serializeEnd = System.nanoTime();
            long sentAt = System.nanoTime();
            var response = requestWithRetry(clientConnection, subject, requestBytes);
            long receivedAt = System.nanoTime();
            long deserializeStart = System.nanoTime();
            var responseMap = OBJECT_MAPPER.readValue(response.getData(), new TypeReference<Map<String, Object>>() {});
            long deserializeEnd = System.nanoTime();
            if (((List<?>) responseMap.get("items")).size() != payload.size()) {
                throw new IllegalStateException("plain-json payload mismatch");
            }
            var serverMetrics = queue.take();
            return sample(serializeEnd - serializeStart, requestBytes.length, serverMetrics.requestNetworkArrivalNs() - sentAt,
                    serverMetrics.serverRequestDeserializationTimeNs(), serverMetrics.serverResponseSerializationTimeNs(),
                    response.getData().length, receivedAt - serverMetrics.responseSentAtNs(), deserializeEnd - deserializeStart);
        });
    }

    private static Runner createProtobufRunner(Connection serverConnection, Connection clientConnection, String subject, Scenario scenario, ArrayBlockingQueue<ServerMetrics> queue) {
        var protobufTypes = PROTO_TYPES.get(scenario.dataShape());
        var dispatcher = serverConnection.createDispatcher(msg -> {
            try {
                long receivedAt = System.nanoTime();
                var request = DynamicMessage.parseFrom(protobufTypes.requestDescriptor(), msg.getData());
                long afterDeserialize = System.nanoTime();
                var responseBuilder = DynamicMessage.newBuilder(protobufTypes.responseDescriptor());
                for (int index = 0; index < request.getRepeatedFieldCount(protobufTypes.requestItemsField()); index += 1) {
                    responseBuilder.addRepeatedField(protobufTypes.responseItemsField(), request.getRepeatedField(protobufTypes.requestItemsField(), index));
                }
                long beforeSerialize = System.nanoTime();
                byte[] responseBytes = responseBuilder.build().toByteArray();
                long responseSentAt = System.nanoTime();
                queue.put(new ServerMetrics(receivedAt, afterDeserialize - receivedAt, responseSentAt - beforeSerialize, responseSentAt));
                serverConnection.publish(msg.getReplyTo(), responseBytes);
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        });
        dispatcher.subscribe(subject);
        return new Runner(dispatcher, payload -> {
            DynamicMessage requestMessage = buildProtobufRequest(protobufTypes, payload);
            long serializeStart = System.nanoTime();
            var requestBytes = requestMessage.toByteArray();
            long serializeEnd = System.nanoTime();
            long sentAt = System.nanoTime();
            var response = requestWithRetry(clientConnection, subject, requestBytes);
            long receivedAt = System.nanoTime();
            long deserializeStart = System.nanoTime();
            var responseMessage = DynamicMessage.parseFrom(protobufTypes.responseDescriptor(), response.getData());
            int responseCount = responseMessage.getRepeatedFieldCount(protobufTypes.responseItemsField());
            long deserializeEnd = System.nanoTime();
            if (responseCount != payload.size()) {
                throw new IllegalStateException("protobuf payload mismatch");
            }
            var serverMetrics = queue.take();
            return sample(serializeEnd - serializeStart, requestBytes.length, serverMetrics.requestNetworkArrivalNs() - sentAt,
                    serverMetrics.serverRequestDeserializationTimeNs(), serverMetrics.serverResponseSerializationTimeNs(),
                    response.getData().length, receivedAt - serverMetrics.responseSentAtNs(), deserializeEnd - deserializeStart);
        });
    }

    private static Runner createTelepactRunner(Connection serverConnection, Connection clientConnection, String subject, Scenario scenario, ArrayBlockingQueue<ServerMetrics> queue) throws Exception {
        var telepactSchema = TelepactSchema.fromDirectory(Path.of("..", "schema", "telepact").toString());
        var state = new HashMap<String, Long>();
        FunctionRoute route = (functionName, requestMessage) -> new Message(Map.of(), Map.of("Ok_", Map.of("items", ((Map<String, Object>) requestMessage.body.get(functionName)).get("items"))));
        var routes = new HashMap<String, FunctionRoute>();
        routes.put("fn.roundTripTypical", route);
        routes.put("fn.roundTripStrings", route);
        routes.put("fn.roundTripNumbers", route);
        var options = new Server.Options();
        options.authRequired = false;
        options.onRequest = message -> state.put("afterDeserializeNs", System.nanoTime());
        options.onResponse = message -> state.put("beforeSerializeNs", System.nanoTime());
        var server = new Server(telepactSchema, new FunctionRouter(routes), options);
        var dispatcher = serverConnection.createDispatcher(msg -> {
            try {
                long receivedAt = System.nanoTime();
                state.clear();
                var response = server.process(msg.getData());
                long responseSentAt = System.nanoTime();
                queue.put(new ServerMetrics(receivedAt, state.getOrDefault("afterDeserializeNs", responseSentAt) - receivedAt,
                        responseSentAt - state.getOrDefault("beforeSerializeNs", receivedAt), responseSentAt));
                serverConnection.publish(msg.getReplyTo(), response.bytes);
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        });
        dispatcher.subscribe(subject);

        final Map<String, Object>[] lastSample = new Map[] { null };
        BiFunction<Message, io.github.telepact.Serializer, Future<Message>> adapter = (message, serializer) -> CompletableFuture.supplyAsync(() -> {
            try {
                long serializeStart = System.nanoTime();
                var requestBytes = serializer.serialize(message);
                long serializeEnd = System.nanoTime();
                long sentAt = System.nanoTime();
                var response = requestWithRetry(clientConnection, subject, requestBytes);
                long receivedAt = System.nanoTime();
                long deserializeStart = System.nanoTime();
                var responseMessage = serializer.deserialize(response.getData());
                long deserializeEnd = System.nanoTime();
                var serverMetrics = queue.take();
                lastSample[0] = sample(serializeEnd - serializeStart, requestBytes.length, serverMetrics.requestNetworkArrivalNs() - sentAt,
                        serverMetrics.serverRequestDeserializationTimeNs(), serverMetrics.serverResponseSerializationTimeNs(),
                        response.getData().length, receivedAt - serverMetrics.responseSentAtNs(), deserializeEnd - deserializeStart);
                return responseMessage;
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        });
        var clientOptions = new Client.Options();
        clientOptions.useBinary = !Objects.equals(scenario.method(), "telepact-json");
        clientOptions.alwaysSendJson = Objects.equals(scenario.method(), "telepact-json");
        var client = new Client(adapter, clientOptions);
        return new Runner(dispatcher, payload -> {
            var headers = Objects.equals(scenario.method(), "telepact-packed-binary") ? new HashMap<String, Object>(Map.of("@pac_", true)) : new HashMap<String, Object>();
            var response = client.request(new Message(headers, Map.of(FUNCTION_NAMES.get(scenario.dataShape()), Map.of("items", payload))));
            var ok = (Map<String, Object>) response.body.get("Ok_");
            if (((List<?>) ok.get("items")).size() != payload.size()) {
                throw new IllegalStateException("telepact payload mismatch");
            }
            return lastSample[0];
        });
    }

    private static Map<String, Object> loadPayloads() throws Exception {
        return OBJECT_MAPPER.readValue(Path.of("..", "payloads", "cases.json").toFile(), new TypeReference<Map<String, Object>>() {});
    }

    private static Map<String, String> parseArgs(String[] args) {
        var parsed = new HashMap<String, String>();
        for (int i = 0; i < args.length; i += 2) {
            parsed.put(args[i].replaceFirst("^--", ""), args[i + 1]);
        }
        return parsed;
    }

    private static io.nats.client.Message requestWithRetry(Connection connection, String subject, byte[] requestBytes) throws Exception {
        for (int attempt = 0; attempt <= NATS_REQUEST_ADDITIONAL_RETRIES; attempt += 1) {
            var response = connection.request(subject, requestBytes, NATS_TIMEOUT);
            if (response != null) {
                return response;
            }
            if (attempt < NATS_REQUEST_ADDITIONAL_RETRIES) {
                Thread.sleep(NATS_RETRY_DELAY.toMillis());
            }
        }
        throw new IllegalStateException("nats request failed");
    }

    private static Map<String, Object> sample(long clientRequestSerializationTimeNs, long serializedRequestSizeBytes,
            long requestNetworkTransitTimeNs, long serverRequestDeserializationTimeNs, long serverResponseSerializationTimeNs,
            long serializedResponseSizeBytes, long responseNetworkTransitTimeNs, long clientResponseDeserializationTimeNs) {
        return Map.of(
                "clientRequestSerializationTimeNs", clientRequestSerializationTimeNs,
                "serializedRequestSizeBytes", serializedRequestSizeBytes,
                "requestNetworkTransitTimeNs", requestNetworkTransitTimeNs,
                "serverRequestDeserializationTimeNs", serverRequestDeserializationTimeNs,
                "serverResponseSerializationTimeNs", serverResponseSerializationTimeNs,
                "serializedResponseSizeBytes", serializedResponseSizeBytes,
                "responseNetworkTransitTimeNs", responseNetworkTransitTimeNs,
                "clientResponseDeserializationTimeNs", clientResponseDeserializationTimeNs);
    }

    private static DynamicMessage buildProtobufRequest(ProtobufTypes protobufTypes, List<Map<String, Object>> payload) {
        var builder = DynamicMessage.newBuilder(protobufTypes.requestDescriptor());
        for (var item : payload) {
            builder.addRepeatedField(protobufTypes.requestItemsField(), buildProtobufItem(protobufTypes.itemDescriptor(), item));
        }
        return builder.build();
    }

    private static DynamicMessage buildProtobufItem(Descriptors.Descriptor itemDescriptor, Map<String, Object> payload) {
        var builder = DynamicMessage.newBuilder(itemDescriptor);
        for (var field : itemDescriptor.getFields()) {
            builder.setField(field, coerceProtobufValue(field, payload.get(field.getName())));
        }
        return builder.build();
    }

    private static Object coerceProtobufValue(Descriptors.FieldDescriptor field, Object value) {
        return switch (field.getType()) {
            case INT64 -> ((Number) value).longValue();
            case DOUBLE -> ((Number) value).doubleValue();
            case STRING -> (String) value;
            default -> throw new IllegalArgumentException("Unsupported protobuf field type: " + field.getType());
        };
    }

    private static Map<String, ProtobufTypes> createProtobufTypes() {
        try {
            var file = DescriptorProtos.FileDescriptorProto.newBuilder()
                    .setName("benchmark.proto")
                    .setPackage("telepact.performance.v1")
                    .setSyntax("proto3");
            addMessage(file, "TypicalItem", List.of(
                    scalarField("accountId", 1, DescriptorProtos.FieldDescriptorProto.Type.TYPE_INT64),
                    scalarField("customerName", 2, DescriptorProtos.FieldDescriptorProto.Type.TYPE_STRING),
                    scalarField("region", 3, DescriptorProtos.FieldDescriptorProto.Type.TYPE_STRING),
                    scalarField("unitPrice", 4, DescriptorProtos.FieldDescriptorProto.Type.TYPE_DOUBLE),
                    scalarField("quantity", 5, DescriptorProtos.FieldDescriptorProto.Type.TYPE_INT64)));
            addMessage(file, "StringItem", List.of(
                    scalarField("code", 1, DescriptorProtos.FieldDescriptorProto.Type.TYPE_STRING),
                    scalarField("city", 2, DescriptorProtos.FieldDescriptorProto.Type.TYPE_STRING),
                    scalarField("country", 3, DescriptorProtos.FieldDescriptorProto.Type.TYPE_STRING),
                    scalarField("segment", 4, DescriptorProtos.FieldDescriptorProto.Type.TYPE_STRING),
                    scalarField("status", 5, DescriptorProtos.FieldDescriptorProto.Type.TYPE_STRING)));
            addMessage(file, "NumberItem", List.of(
                    scalarField("accountId", 1, DescriptorProtos.FieldDescriptorProto.Type.TYPE_INT64),
                    scalarField("visits", 2, DescriptorProtos.FieldDescriptorProto.Type.TYPE_INT64),
                    scalarField("score", 3, DescriptorProtos.FieldDescriptorProto.Type.TYPE_DOUBLE),
                    scalarField("balance", 4, DescriptorProtos.FieldDescriptorProto.Type.TYPE_DOUBLE),
                    scalarField("ratio", 5, DescriptorProtos.FieldDescriptorProto.Type.TYPE_DOUBLE)));
            addMessage(file, "TypicalRequest", List.of(repeatedMessageField("items", 1, "telepact.performance.v1.TypicalItem")));
            addMessage(file, "TypicalResponse", List.of(repeatedMessageField("items", 1, "telepact.performance.v1.TypicalItem")));
            addMessage(file, "StringsRequest", List.of(repeatedMessageField("items", 1, "telepact.performance.v1.StringItem")));
            addMessage(file, "StringsResponse", List.of(repeatedMessageField("items", 1, "telepact.performance.v1.StringItem")));
            addMessage(file, "NumbersRequest", List.of(repeatedMessageField("items", 1, "telepact.performance.v1.NumberItem")));
            addMessage(file, "NumbersResponse", List.of(repeatedMessageField("items", 1, "telepact.performance.v1.NumberItem")));

            var descriptor = Descriptors.FileDescriptor.buildFrom(file.build(), new Descriptors.FileDescriptor[0]);
            return Map.of(
                    "typical", protobufTypesFor(descriptor, "TypicalRequest", "TypicalResponse", "TypicalItem"),
                    "all-strings", protobufTypesFor(descriptor, "StringsRequest", "StringsResponse", "StringItem"),
                    "all-numbers", protobufTypesFor(descriptor, "NumbersRequest", "NumbersResponse", "NumberItem"));
        } catch (Descriptors.DescriptorValidationException e) {
            throw new ExceptionInInitializerError(e);
        }
    }

    private static ProtobufTypes protobufTypesFor(Descriptors.FileDescriptor descriptor, String requestName, String responseName, String itemName) {
        var requestDescriptor = descriptor.findMessageTypeByName(requestName);
        var responseDescriptor = descriptor.findMessageTypeByName(responseName);
        var itemDescriptor = descriptor.findMessageTypeByName(itemName);
        return new ProtobufTypes(
                requestDescriptor,
                requestDescriptor.findFieldByName("items"),
                responseDescriptor,
                responseDescriptor.findFieldByName("items"),
                itemDescriptor);
    }

    private static void addMessage(
            DescriptorProtos.FileDescriptorProto.Builder file,
            String name,
            List<DescriptorProtos.FieldDescriptorProto> fields) {
        var message = file.addMessageTypeBuilder().setName(name);
        for (var field : fields) {
            message.addField(field);
        }
    }

    private static DescriptorProtos.FieldDescriptorProto scalarField(
            String name,
            int number,
            DescriptorProtos.FieldDescriptorProto.Type type) {
        return DescriptorProtos.FieldDescriptorProto.newBuilder()
                .setName(name)
                .setNumber(number)
                .setLabel(DescriptorProtos.FieldDescriptorProto.Label.LABEL_OPTIONAL)
                .setType(type)
                .build();
    }

    private static DescriptorProtos.FieldDescriptorProto repeatedMessageField(String name, int number, String typeName) {
        return DescriptorProtos.FieldDescriptorProto.newBuilder()
                .setName(name)
                .setNumber(number)
                .setLabel(DescriptorProtos.FieldDescriptorProto.Label.LABEL_REPEATED)
                .setType(DescriptorProtos.FieldDescriptorProto.Type.TYPE_MESSAGE)
                .setTypeName("." + typeName)
                .build();
    }

    private record Runner(Dispatcher dispatcher, Requester requester) {
        Map<String, Object> requestOnce(List<Map<String, Object>> payload) throws Exception {
            return requester.requestOnce(payload);
        }

        void close() throws Exception {
            dispatcher.drain(Duration.ofSeconds(1)).get();
        }
    }

    @FunctionalInterface
    private interface Requester {
        Map<String, Object> requestOnce(List<Map<String, Object>> payload) throws Exception;
    }
}
