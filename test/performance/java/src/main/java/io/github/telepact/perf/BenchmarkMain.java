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

package io.github.telepact.perf;

import java.io.File;
import java.io.IOException;
import java.nio.file.Path;
import java.time.Duration;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.CompletableFuture;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import io.github.telepact.Client;
import io.github.telepact.FunctionRoute;
import io.github.telepact.FunctionRouter;
import io.github.telepact.Message;
import io.github.telepact.Server;
import io.github.telepact.TelepactSchema;
import io.nats.client.Connection;
import io.nats.client.Dispatcher;
import io.nats.client.Nats;
import io.nats.client.impl.Headers;
import telepact.performance.Benchmark.AllNumbersItem;
import telepact.performance.Benchmark.AllNumbersRequest;
import telepact.performance.Benchmark.AllNumbersResponse;
import telepact.performance.Benchmark.AllStringsItem;
import telepact.performance.Benchmark.AllStringsRequest;
import telepact.performance.Benchmark.AllStringsResponse;
import telepact.performance.Benchmark.TypicalItem;
import telepact.performance.Benchmark.TypicalRequest;
import telepact.performance.Benchmark.TypicalResponse;

public class BenchmarkMain {
    private static final Path ROOT = Path.of("/home/runner/work/telepact/telepact/test/performance");
    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();
    private static final TypeReference<Map<String, Object>> MAP_TYPE = new TypeReference<>() {};
    private static final String LANGUAGE = "java";
    private static final Map<String, String> SERVER_HEADER_NAMES = Map.of(
            "receivedWallNs", "x-telepact-perf-server-received-wall-ns",
            "requestDeserializeNs", "x-telepact-perf-server-request-deserialize-ns",
            "responseSerializeNs", "x-telepact-perf-server-response-serialize-ns",
            "sentWallNs", "x-telepact-perf-server-sent-wall-ns");

    static class ServerMeasurement {
        long startPerfNs;
        long receivedWallNs;
        long requestDeserializeNs;
        long serializeStartNs;
        long responseSerializeNs;
        long sentWallNs;
    }

    public static void main(String[] args) throws Exception {
        String outputPath = null;
        for (int index = 0; index < args.length; index += 1) {
            if (Objects.equals(args[index], "--output") && index + 1 < args.length) {
                outputPath = args[index + 1];
            }
        }
        if (outputPath == null) {
            throw new IllegalArgumentException("Expected --output <path>");
        }

        Map<String, Object> config = readJson(ROOT.resolve("config/benchmark-config.json").toFile());
        Map<String, Object> payloads = readJson(ROOT.resolve("config/payloads.json").toFile());

        String natsUrl = System.getenv().getOrDefault("NATS_URL", (String) config.get("natsUrl"));
        try (Connection connection = Nats.connect(natsUrl)) {
            List<Dispatcher> dispatchers = startServers(connection, config, payloads);
            List<Map<String, Object>> cases = new ArrayList<>();
            try {
                @SuppressWarnings("unchecked")
                var dataShapes = (Map<String, Object>) config.get("dataShapes");
                @SuppressWarnings("unchecked")
                var collectionShapes = (Map<String, Object>) config.get("collectionShapes");
                for (String dataShape : dataShapes.keySet()) {
                    for (String collectionShape : collectionShapes.keySet()) {
                        cases.add(runTelepactCase(connection, config, payloads, "telepact_json", dataShape, collectionShape));
                        cases.add(runTelepactCase(connection, config, payloads, "telepact_binary", dataShape, collectionShape));
                        cases.add(runTelepactCase(connection, config, payloads, "telepact_packed_binary", dataShape, collectionShape));
                        cases.add(runProtobufCase(connection, config, payloads, dataShape, collectionShape));
                        cases.add(runPlainJsonCase(connection, config, payloads, dataShape, collectionShape));
                    }
                }
            } finally {
                connection.flush(Duration.ofSeconds(2));
            }

            Map<String, Object> output = new LinkedHashMap<>();
            output.put("language", LANGUAGE);
            output.put("nats_url", natsUrl);
            output.put("cases", cases);
            OBJECT_MAPPER.writerWithDefaultPrettyPrinter().writeValue(new File(outputPath), output);
        }
    }

    private static List<Dispatcher> startServers(Connection connection, Map<String, Object> config, Map<String, Object> payloads) throws Exception {
        List<Dispatcher> dispatchers = new ArrayList<>();
        TelepactSchema schema = TelepactSchema.fromFileJsonMap(Map.of(
                "benchmark.telepact.json",
                java.nio.file.Files.readString(ROOT.resolve("schema/benchmark.telepact.json"))));
        final ServerMeasurement[] currentTelepactMeasurement = new ServerMeasurement[1];

        Server.Options options = new Server.Options();
        options.authRequired = false;
        options.onRequest = (_message) -> {
            if (currentTelepactMeasurement[0] != null) {
                currentTelepactMeasurement[0].requestDeserializeNs = System.nanoTime() - currentTelepactMeasurement[0].startPerfNs;
            }
        };
        options.onResponse = (_message) -> {
            if (currentTelepactMeasurement[0] != null) {
                currentTelepactMeasurement[0].serializeStartNs = System.nanoTime();
            }
        };

        FunctionRoute route = (_functionName, requestMessage) -> new Message(Map.of(), Map.of("Ok_", deepCopyMap(requestMessage.getBodyPayload())));
        Server telepactServer = new Server(schema, new FunctionRouter(new LinkedHashMap<>(Map.of(
                "fn.echoTypical", route,
                "fn.echoAllStrings", route,
                "fn.echoAllNumbers", route))), options);

        @SuppressWarnings("unchecked")
        var dataShapes = (Map<String, Object>) config.get("dataShapes");
        for (String method : List.of("telepact_json", "telepact_binary", "telepact_packed_binary")) {
            for (String dataShape : dataShapes.keySet()) {
                String subject = subjectFor(config, method, dataShape);
                Dispatcher dispatcher = connection.createDispatcher((msg) -> {
                    try {
                        ServerMeasurement measurement = new ServerMeasurement();
                        measurement.startPerfNs = System.nanoTime();
                        measurement.receivedWallNs = nowWallNs();
                        currentTelepactMeasurement[0] = measurement;
                        var response = telepactServer.process(msg.getData());
                        measurement.responseSerializeNs = System.nanoTime() - (measurement.serializeStartNs == 0L ? System.nanoTime() : measurement.serializeStartNs);
                        measurement.sentWallNs = nowWallNs();
                        currentTelepactMeasurement[0] = null;
                        connection.publish(msg.getReplyTo(), metricHeaders(measurement), response.bytes);
                    } catch (Exception ex) {
                        throw new RuntimeException(ex);
                    }
                });
                dispatcher.subscribe(subject);
                dispatchers.add(dispatcher);
            }
        }

        for (String dataShape : dataShapes.keySet()) {
            String jsonSubject = subjectFor(config, "plain_json", dataShape);
            Dispatcher jsonDispatcher = connection.createDispatcher((msg) -> {
                try {
                    ServerMeasurement measurement = new ServerMeasurement();
                    measurement.receivedWallNs = nowWallNs();
                    long deserializeStartNs = System.nanoTime();
                    var requestPayload = OBJECT_MAPPER.readValue(msg.getData(), MAP_TYPE);
                    measurement.requestDeserializeNs = System.nanoTime() - deserializeStartNs;
                    long serializeStartNs = System.nanoTime();
                    byte[] responseBytes = OBJECT_MAPPER.writeValueAsBytes(requestPayload);
                    measurement.responseSerializeNs = System.nanoTime() - serializeStartNs;
                    measurement.sentWallNs = nowWallNs();
                    connection.publish(msg.getReplyTo(), metricHeaders(measurement), responseBytes);
                } catch (Exception ex) {
                    throw new RuntimeException(ex);
                }
            });
            jsonDispatcher.subscribe(jsonSubject);
            dispatchers.add(jsonDispatcher);

            String protobufSubject = subjectFor(config, "protobuf", dataShape);
            Dispatcher protobufDispatcher = connection.createDispatcher((msg) -> {
                try {
                    ServerMeasurement measurement = new ServerMeasurement();
                    measurement.receivedWallNs = nowWallNs();
                    long deserializeStartNs = System.nanoTime();
                    byte[] responseBytes;
                    switch (dataShape) {
                        case "typical_data" -> {
                            TypicalRequest request = TypicalRequest.parseFrom(msg.getData());
                            measurement.requestDeserializeNs = System.nanoTime() - deserializeStartNs;
                            long serializeStartNs = System.nanoTime();
                            responseBytes = TypicalResponse.newBuilder().addAllItems(request.getItemsList()).build().toByteArray();
                            measurement.responseSerializeNs = System.nanoTime() - serializeStartNs;
                        }
                        case "all_strings" -> {
                            AllStringsRequest request = AllStringsRequest.parseFrom(msg.getData());
                            measurement.requestDeserializeNs = System.nanoTime() - deserializeStartNs;
                            long serializeStartNs = System.nanoTime();
                            responseBytes = AllStringsResponse.newBuilder().addAllItems(request.getItemsList()).build().toByteArray();
                            measurement.responseSerializeNs = System.nanoTime() - serializeStartNs;
                        }
                        case "all_numbers" -> {
                            AllNumbersRequest request = AllNumbersRequest.parseFrom(msg.getData());
                            measurement.requestDeserializeNs = System.nanoTime() - deserializeStartNs;
                            long serializeStartNs = System.nanoTime();
                            responseBytes = AllNumbersResponse.newBuilder().addAllItems(request.getItemsList()).build().toByteArray();
                            measurement.responseSerializeNs = System.nanoTime() - serializeStartNs;
                        }
                        default -> throw new IllegalArgumentException(dataShape);
                    }
                    measurement.sentWallNs = nowWallNs();
                    connection.publish(msg.getReplyTo(), metricHeaders(measurement), responseBytes);
                } catch (Exception ex) {
                    throw new RuntimeException(ex);
                }
            });
            protobufDispatcher.subscribe(protobufSubject);
            dispatchers.add(protobufDispatcher);
        }

        connection.flush(Duration.ofSeconds(2));
        return dispatchers;
    }

    private static Map<String, Object> runTelepactCase(Connection connection, Map<String, Object> config, Map<String, Object> payloads,
            String method, String dataShape, String collectionShape) throws Exception {
        Map<String, Object> payload = nestedPayload(payloads, dataShape, collectionShape);
        @SuppressWarnings("unchecked")
        String functionName = (String) ((Map<String, Object>) ((Map<String, Object>) config.get("dataShapes")).get(dataShape)).get("telepactFunction");
        boolean useBinary = !Objects.equals(method, "telepact_json");
        boolean packed = Objects.equals(method, "telepact_packed_binary");
        int handshakeIterations = useBinary ? ((Number) config.get("binaryNegotiationWarmupIterations")).intValue() : 0;
        int warmupIterations = ((Number) config.get("warmupIterations")).intValue();
        int steadyStateIterations = ((Number) config.get("steadyStateIterations")).intValue();
        long timeoutMs = ((Number) config.get("requestTimeoutMs")).longValue();
        List<Map<String, Object>> samples = new ArrayList<>();

        Client.Options options = new Client.Options();
        options.useBinary = useBinary;
        options.alwaysSendJson = !useBinary;
        Client client = new Client((requestMessage, serializer) -> CompletableFuture.supplyAsync(() -> {
            try {
                long requestStartNs = System.nanoTime();
                byte[] requestBytes = serializer.serialize(requestMessage);
                long requestSerializeNs = System.nanoTime() - requestStartNs;
                long requestSentWallNs = nowWallNs();
                io.nats.client.Message responseMsg = connection.request(subjectFor(config, method, dataShape), requestBytes, Duration.ofMillis(timeoutMs));
                long responseReceivedWallNs = nowWallNs();
                Map<String, Long> serverMetrics = parseMetricHeaders(responseMsg.getHeaders());
                long responseDeserializeStartNs = System.nanoTime();
                Message response = serializer.deserialize(responseMsg.getData());
                long responseDeserializeNs = System.nanoTime() - responseDeserializeStartNs;
                samples.add(sampleFromTimings(requestSerializeNs, requestBytes.length, requestSentWallNs, serverMetrics,
                        responseMsg.getData().length, responseReceivedWallNs, responseDeserializeNs,
                        System.nanoTime() - requestStartNs));
                return response;
            } catch (Exception ex) {
                throw new RuntimeException(ex);
            }
        }), options);

        int totalIterations = handshakeIterations + warmupIterations + steadyStateIterations;
        for (int index = 0; index < totalIterations; index += 1) {
            Message response = client.request(telepactMessage(functionName, payload, packed));
            if (!Objects.equals(response.body, Map.of("Ok_", payload))) {
                throw new IllegalStateException("Unexpected Telepact response for " + method + "/" + dataShape + "/" + collectionShape);
            }
        }

        return Map.of(
                "language", LANGUAGE,
                "method", method,
                "data_shape", dataShape,
                "collection_shape", collectionShape,
                "samples", samples.subList(handshakeIterations + warmupIterations, samples.size()));
    }

    private static Map<String, Object> runPlainJsonCase(Connection connection, Map<String, Object> config, Map<String, Object> payloads,
            String dataShape, String collectionShape) throws Exception {
        Map<String, Object> payload = nestedPayload(payloads, dataShape, collectionShape);
        int warmupIterations = ((Number) config.get("warmupIterations")).intValue();
        int steadyStateIterations = ((Number) config.get("steadyStateIterations")).intValue();
        long timeoutMs = ((Number) config.get("requestTimeoutMs")).longValue();
        List<Map<String, Object>> samples = new ArrayList<>();
        for (int index = 0; index < warmupIterations + steadyStateIterations; index += 1) {
            long requestStartNs = System.nanoTime();
            byte[] requestBytes = OBJECT_MAPPER.writeValueAsBytes(payload);
            long requestSerializeNs = System.nanoTime() - requestStartNs;
            long requestSentWallNs = nowWallNs();
            io.nats.client.Message responseMsg = connection.request(subjectFor(config, "plain_json", dataShape), requestBytes, Duration.ofMillis(timeoutMs));
            long responseReceivedWallNs = nowWallNs();
            Map<String, Long> serverMetrics = parseMetricHeaders(responseMsg.getHeaders());
            long responseDeserializeStartNs = System.nanoTime();
            Map<String, Object> parsedResponse = OBJECT_MAPPER.readValue(responseMsg.getData(), MAP_TYPE);
            long responseDeserializeNs = System.nanoTime() - responseDeserializeStartNs;
            if (!Objects.equals(parsedResponse, payload)) {
                throw new IllegalStateException("Unexpected JSON response for " + dataShape + "/" + collectionShape);
            }
            samples.add(sampleFromTimings(requestSerializeNs, requestBytes.length, requestSentWallNs, serverMetrics,
                    responseMsg.getData().length, responseReceivedWallNs, responseDeserializeNs, System.nanoTime() - requestStartNs));
        }
        return Map.of(
                "language", LANGUAGE,
                "method", "plain_json",
                "data_shape", dataShape,
                "collection_shape", collectionShape,
                "samples", samples.subList(warmupIterations, samples.size()));
    }

    private static Map<String, Object> runProtobufCase(Connection connection, Map<String, Object> config, Map<String, Object> payloads,
            String dataShape, String collectionShape) throws Exception {
        Map<String, Object> payload = nestedPayload(payloads, dataShape, collectionShape);
        Map<String, Object> normalizedPayload = normalizePayloadForProtobuf(dataShape, payload);
        int warmupIterations = ((Number) config.get("warmupIterations")).intValue();
        int steadyStateIterations = ((Number) config.get("steadyStateIterations")).intValue();
        long timeoutMs = ((Number) config.get("requestTimeoutMs")).longValue();
        List<Map<String, Object>> samples = new ArrayList<>();

        byte[] baselineRequestBytes = protobufRequestBytes(dataShape, payload);
        if (!Objects.equals(protobufResponsePayload(dataShape, baselineRequestBytes), normalizedPayload)) {
            throw new IllegalStateException("Protobuf payload mismatch for " + dataShape + "/" + collectionShape);
        }

        for (int index = 0; index < warmupIterations + steadyStateIterations; index += 1) {
            long requestStartNs = System.nanoTime();
            byte[] requestBytes = protobufRequestBytes(dataShape, payload);
            long requestSerializeNs = System.nanoTime() - requestStartNs;
            long requestSentWallNs = nowWallNs();
            io.nats.client.Message responseMsg = connection.request(subjectFor(config, "protobuf", dataShape), requestBytes, Duration.ofMillis(timeoutMs));
            long responseReceivedWallNs = nowWallNs();
            Map<String, Long> serverMetrics = parseMetricHeaders(responseMsg.getHeaders());
            long responseDeserializeStartNs = System.nanoTime();
            Map<String, Object> responsePayload = protobufResponsePayload(dataShape, responseMsg.getData());
            long responseDeserializeNs = System.nanoTime() - responseDeserializeStartNs;
            if (!Objects.equals(responsePayload, normalizedPayload)) {
                throw new IllegalStateException("Unexpected protobuf response for " + dataShape + "/" + collectionShape);
            }
            samples.add(sampleFromTimings(requestSerializeNs, requestBytes.length, requestSentWallNs, serverMetrics,
                    responseMsg.getData().length, responseReceivedWallNs, responseDeserializeNs, System.nanoTime() - requestStartNs));
        }

        return Map.of(
                "language", LANGUAGE,
                "method", "protobuf",
                "data_shape", dataShape,
                "collection_shape", collectionShape,
                "samples", samples.subList(warmupIterations, samples.size()));
    }

    private static byte[] protobufRequestBytes(String dataShape, Map<String, Object> payload) {
        return switch (dataShape) {
            case "typical_data" -> buildTypicalRequest(payload).toByteArray();
            case "all_strings" -> buildAllStringsRequest(payload).toByteArray();
            case "all_numbers" -> buildAllNumbersRequest(payload).toByteArray();
            default -> throw new IllegalArgumentException(dataShape);
        };
    }

    private static Map<String, Object> protobufResponsePayload(String dataShape, byte[] bytes) throws Exception {
        return switch (dataShape) {
            case "typical_data" -> typicalResponsePayload(TypicalResponse.parseFrom(bytes));
            case "all_strings" -> allStringsResponsePayload(AllStringsResponse.parseFrom(bytes));
            case "all_numbers" -> allNumbersResponsePayload(AllNumbersResponse.parseFrom(bytes));
            default -> throw new IllegalArgumentException(dataShape);
        };
    }

    private static Map<String, Object> normalizePayloadForProtobuf(String dataShape, Map<String, Object> payload) throws Exception {
        return protobufResponsePayload(dataShape, protobufRequestBytes(dataShape, payload));
    }

    private static TypicalRequest buildTypicalRequest(Map<String, Object> payload) {
        TypicalRequest.Builder builder = TypicalRequest.newBuilder();
        for (Map<String, Object> item : itemMaps(payload)) {
            builder.addItems(TypicalItem.newBuilder()
                    .setPrimaryText((String) item.get("primaryText"))
                    .setSecondaryText((String) item.get("secondaryText"))
                    .setPrimaryInt(((Number) item.get("primaryInt")).longValue())
                    .setSecondaryInt(((Number) item.get("secondaryInt")).longValue())
                    .setPrimaryNumber(((Number) item.get("primaryNumber")).doubleValue())
                    .setSecondaryNumber(((Number) item.get("secondaryNumber")).doubleValue())
                    .build());
        }
        return builder.build();
    }

    private static AllStringsRequest buildAllStringsRequest(Map<String, Object> payload) {
        AllStringsRequest.Builder builder = AllStringsRequest.newBuilder();
        for (Map<String, Object> item : itemMaps(payload)) {
            builder.addItems(AllStringsItem.newBuilder()
                    .setAlpha((String) item.get("alpha"))
                    .setBeta((String) item.get("beta"))
                    .setGamma((String) item.get("gamma"))
                    .setDelta((String) item.get("delta"))
                    .setEpsilon((String) item.get("epsilon"))
                    .setZeta((String) item.get("zeta"))
                    .build());
        }
        return builder.build();
    }

    private static AllNumbersRequest buildAllNumbersRequest(Map<String, Object> payload) {
        AllNumbersRequest.Builder builder = AllNumbersRequest.newBuilder();
        for (Map<String, Object> item : itemMaps(payload)) {
            builder.addItems(AllNumbersItem.newBuilder()
                    .setFirstInt(((Number) item.get("firstInt")).longValue())
                    .setSecondInt(((Number) item.get("secondInt")).longValue())
                    .setThirdInt(((Number) item.get("thirdInt")).longValue())
                    .setFirstNumber(((Number) item.get("firstNumber")).doubleValue())
                    .setSecondNumber(((Number) item.get("secondNumber")).doubleValue())
                    .setThirdNumber(((Number) item.get("thirdNumber")).doubleValue())
                    .build());
        }
        return builder.build();
    }

    private static Map<String, Object> typicalResponsePayload(TypicalResponse response) {
        List<Map<String, Object>> items = new ArrayList<>();
        for (TypicalItem item : response.getItemsList()) {
            items.add(Map.of(
                    "primaryText", item.getPrimaryText(),
                    "secondaryText", item.getSecondaryText(),
                    "primaryInt", item.getPrimaryInt(),
                    "secondaryInt", item.getSecondaryInt(),
                    "primaryNumber", item.getPrimaryNumber(),
                    "secondaryNumber", item.getSecondaryNumber()));
        }
        return Map.of("items", items);
    }

    private static Map<String, Object> allStringsResponsePayload(AllStringsResponse response) {
        List<Map<String, Object>> items = new ArrayList<>();
        for (AllStringsItem item : response.getItemsList()) {
            items.add(Map.of(
                    "alpha", item.getAlpha(),
                    "beta", item.getBeta(),
                    "gamma", item.getGamma(),
                    "delta", item.getDelta(),
                    "epsilon", item.getEpsilon(),
                    "zeta", item.getZeta()));
        }
        return Map.of("items", items);
    }

    private static Map<String, Object> allNumbersResponsePayload(AllNumbersResponse response) {
        List<Map<String, Object>> items = new ArrayList<>();
        for (AllNumbersItem item : response.getItemsList()) {
            items.add(Map.of(
                    "firstInt", item.getFirstInt(),
                    "secondInt", item.getSecondInt(),
                    "thirdInt", item.getThirdInt(),
                    "firstNumber", item.getFirstNumber(),
                    "secondNumber", item.getSecondNumber(),
                    "thirdNumber", item.getThirdNumber()));
        }
        return Map.of("items", items);
    }

    @SuppressWarnings("unchecked")
    private static List<Map<String, Object>> itemMaps(Map<String, Object> payload) {
        return (List<Map<String, Object>>) payload.get("items");
    }

    @SuppressWarnings("unchecked")
    private static Map<String, Object> nestedPayload(Map<String, Object> payloads, String dataShape, String collectionShape) {
        return deepCopyMap((Map<String, Object>) ((Map<String, Object>) payloads.get(dataShape)).get(collectionShape));
    }

    private static Message telepactMessage(String functionName, Map<String, Object> payload, boolean packed) {
        Map<String, Object> headers = packed ? new LinkedHashMap<>(Map.of("@pac_", true)) : new LinkedHashMap<>();
        return new Message(headers, Map.of(functionName, deepCopyMap(payload)));
    }

    private static String subjectFor(Map<String, Object> config, String method, String dataShape) {
        @SuppressWarnings("unchecked")
        Map<String, Object> dataShapeConfig = (Map<String, Object>) ((Map<String, Object>) config.get("dataShapes")).get(dataShape);
        return "%s.%s.%s.%s".formatted(config.get("subjectPrefix"), LANGUAGE, method, dataShapeConfig.get("subjectSuffix"));
    }

    private static Headers metricHeaders(ServerMeasurement measurement) {
        Headers headers = new Headers();
        headers.add(SERVER_HEADER_NAMES.get("receivedWallNs"), Long.toString(measurement.receivedWallNs));
        headers.add(SERVER_HEADER_NAMES.get("requestDeserializeNs"), Long.toString(measurement.requestDeserializeNs));
        headers.add(SERVER_HEADER_NAMES.get("responseSerializeNs"), Long.toString(measurement.responseSerializeNs));
        headers.add(SERVER_HEADER_NAMES.get("sentWallNs"), Long.toString(measurement.sentWallNs));
        return headers;
    }

    private static Map<String, Long> parseMetricHeaders(Headers headers) {
        return Map.of(
                "receivedWallNs", Long.parseLong(headers.getFirst(SERVER_HEADER_NAMES.get("receivedWallNs"))),
                "requestDeserializeNs", Long.parseLong(headers.getFirst(SERVER_HEADER_NAMES.get("requestDeserializeNs"))),
                "responseSerializeNs", Long.parseLong(headers.getFirst(SERVER_HEADER_NAMES.get("responseSerializeNs"))),
                "sentWallNs", Long.parseLong(headers.getFirst(SERVER_HEADER_NAMES.get("sentWallNs"))));
    }

    private static Map<String, Object> sampleFromTimings(long requestSerializeNs, int requestSizeBytes, long requestSentWallNs,
            Map<String, Long> serverMetrics, int responseSizeBytes, long responseReceivedWallNs, long responseDeserializeNs,
            long roundTripNs) {
        return Map.of(
                "client_request_serialize_ns", requestSerializeNs,
                "request_size_bytes", requestSizeBytes,
                "request_network_transit_ns", Math.max(0L, serverMetrics.get("receivedWallNs") - requestSentWallNs),
                "server_request_deserialize_ns", serverMetrics.get("requestDeserializeNs"),
                "server_response_serialize_ns", serverMetrics.get("responseSerializeNs"),
                "response_size_bytes", responseSizeBytes,
                "response_network_transit_ns", Math.max(0L, responseReceivedWallNs - serverMetrics.get("sentWallNs")),
                "client_response_deserialize_ns", responseDeserializeNs,
                "round_trip_ns", roundTripNs);
    }

    private static long nowWallNs() {
        return System.currentTimeMillis() * 1_000_000L;
    }

    private static Map<String, Object> readJson(File file) throws IOException {
        return OBJECT_MAPPER.readValue(file, MAP_TYPE);
    }

    @SuppressWarnings("unchecked")
    private static Map<String, Object> deepCopyMap(Map<String, Object> value) {
        return OBJECT_MAPPER.convertValue(value, MAP_TYPE);
    }
}
