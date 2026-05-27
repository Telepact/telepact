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
import com.google.protobuf.MessageLite;
import io.github.telepact.Message;
import io.github.telepact.SerializerFactory;
import io.github.telepact.TelepactSchema;
import java.io.File;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import telepact.performance.v1.Benchmark;

public class Main {
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
    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

    record Scenario(String dataShape, String collectionShape, String method) {}

    public static void main(String[] args) throws Exception {
        var parsed = parseArgs(args);
        var iterations = Integer.parseInt(parsed.get("iterations"));
        var warmupIterations = Integer.parseInt(parsed.get("warmup-iterations"));
        var dataShapes = parseCsv(parsed.get("data-shapes"), DATA_SHAPES);
        var collectionShapes = parseCsv(parsed.get("collection-shapes"), COLLECTION_SHAPES);
        var methods = parseCsv(parsed.get("methods"), METHODS);
        var output = parsed.get("output");
        var payloads = loadPayloads();
        var scenarios = new ArrayList<Object>();

        for (var dataShape : dataShapes) {
            for (var collectionShape : collectionShapes) {
                for (var method : methods) {
                    var scenario = new Scenario(dataShape, collectionShape, method);
                    var payload = (List<Map<String, Object>>) ((Map<String, Object>) payloads.get(dataShape)).get(collectionShape);
                    var benchmark = createBenchmark(scenario);
                    var scenarioWarmupIterations = warmupIterationsForScenario(scenario, warmupIterations);
                    for (int i = 0; i < scenarioWarmupIterations; i += 1) {
                        benchmark.run(payload);
                    }
                    var samples = new ArrayList<Object>();
                    for (int i = 0; i < iterations; i += 1) {
                        samples.add(benchmark.run(payload));
                    }
                    scenarios.add(Map.of(
                            "language", "java",
                            "dataShape", dataShape,
                            "collectionShape", collectionShape,
                            "method", method,
                            "iterations", iterations,
                            "warmupIterations", scenarioWarmupIterations,
                            "samples", samples));
                }
            }
        }

        OBJECT_MAPPER.writeValue(new File(output), Map.of(
                "metadata", Map.of(
                        "language", "java",
                        "generatedAt", java.time.OffsetDateTime.now().toString(),
                        "iterations", iterations,
                        "warmupIterations", warmupIterations,
                        "dataShapes", dataShapes,
                        "collectionShapes", collectionShapes,
                        "methods", methods),
                "scenarios", scenarios));
    }

    private static int warmupIterationsForScenario(Scenario scenario, int warmupIterations) {
        if (Objects.equals(scenario.method(), "telepact-binary") || Objects.equals(scenario.method(), "telepact-packed-binary")) {
            return warmupIterations;
        }
        return 0;
    }

    private static BenchmarkRun createBenchmark(Scenario scenario) throws Exception {
        return switch (scenario.method()) {
            case "plain-json" -> createPlainJsonBenchmark(scenario);
            case "protobuf" -> createProtobufBenchmark(scenario);
            default -> createTelepactBenchmark(scenario);
        };
    }

    private static BenchmarkRun createPlainJsonBenchmark(Scenario scenario) {
        return payload -> {
            var request = Map.of("function", PLAIN_FUNCTION_NAMES.get(scenario.dataShape()), "items", payload);
            long requestSerializeStart = System.nanoTime();
            var requestBytes = OBJECT_MAPPER.writeValueAsBytes(request);
            long requestSerializeEnd = System.nanoTime();
            long requestDeserializeStart = System.nanoTime();
            var requestRoundTrip = OBJECT_MAPPER.readValue(requestBytes, new TypeReference<Map<String, Object>>() {});
            long requestDeserializeEnd = System.nanoTime();
            if (!Objects.equals(requestRoundTrip.get("items"), payload)) {
                throw new IllegalStateException("plain-json payload mismatch");
            }

            var response = Map.of("function", requestRoundTrip.get("function"), "items", requestRoundTrip.get("items"));
            long responseSerializeStart = System.nanoTime();
            var responseBytes = OBJECT_MAPPER.writeValueAsBytes(response);
            long responseSerializeEnd = System.nanoTime();
            long responseDeserializeStart = System.nanoTime();
            var responseRoundTrip = OBJECT_MAPPER.readValue(responseBytes, new TypeReference<Map<String, Object>>() {});
            long responseDeserializeEnd = System.nanoTime();
            if (!Objects.equals(responseRoundTrip.get("items"), payload)) {
                throw new IllegalStateException("plain-json response mismatch");
            }

            return sample(
                    requestSerializeEnd - requestSerializeStart,
                    requestDeserializeEnd - requestDeserializeStart,
                    responseSerializeEnd - responseSerializeStart,
                    responseDeserializeEnd - responseDeserializeStart,
                    requestBytes.length,
                    responseBytes.length);
        };
    }

    private static BenchmarkRun createProtobufBenchmark(Scenario scenario) {
        return payload -> {
            MessageLite requestMessage;
            switch (scenario.dataShape()) {
                case "typical" -> requestMessage = buildTypicalRequest(payload);
                case "all-strings" -> requestMessage = buildStringsRequest(payload);
                default -> requestMessage = buildNumbersRequest(payload);
            }

            long requestSerializeStart = System.nanoTime();
            var requestBytes = requestMessage.toByteArray();
            long requestSerializeEnd = System.nanoTime();
            long requestDeserializeStart = System.nanoTime();
            MessageLite requestRoundTrip;
            switch (scenario.dataShape()) {
                case "typical" -> requestRoundTrip = Benchmark.TypicalRequest.parseFrom(requestBytes);
                case "all-strings" -> requestRoundTrip = Benchmark.StringsRequest.parseFrom(requestBytes);
                default -> requestRoundTrip = Benchmark.NumbersRequest.parseFrom(requestBytes);
            }
            long requestDeserializeEnd = System.nanoTime();

            MessageLite responseMessage;
            int requestCount;
            switch (scenario.dataShape()) {
                case "typical" -> {
                    var typedRequest = (Benchmark.TypicalRequest) requestRoundTrip;
                    requestCount = typedRequest.getItemsCount();
                    responseMessage = Benchmark.TypicalResponse.newBuilder().addAllItems(typedRequest.getItemsList()).build();
                }
                case "all-strings" -> {
                    var typedRequest = (Benchmark.StringsRequest) requestRoundTrip;
                    requestCount = typedRequest.getItemsCount();
                    responseMessage = Benchmark.StringsResponse.newBuilder().addAllItems(typedRequest.getItemsList()).build();
                }
                default -> {
                    var typedRequest = (Benchmark.NumbersRequest) requestRoundTrip;
                    requestCount = typedRequest.getItemsCount();
                    responseMessage = Benchmark.NumbersResponse.newBuilder().addAllItems(typedRequest.getItemsList()).build();
                }
            }
            if (requestCount != payload.size()) {
                throw new IllegalStateException("protobuf payload mismatch");
            }

            long responseSerializeStart = System.nanoTime();
            var responseBytes = responseMessage.toByteArray();
            long responseSerializeEnd = System.nanoTime();
            long responseDeserializeStart = System.nanoTime();
            int responseCount;
            switch (scenario.dataShape()) {
                case "typical" -> responseCount = Benchmark.TypicalResponse.parseFrom(responseBytes).getItemsCount();
                case "all-strings" -> responseCount = Benchmark.StringsResponse.parseFrom(responseBytes).getItemsCount();
                default -> responseCount = Benchmark.NumbersResponse.parseFrom(responseBytes).getItemsCount();
            }
            long responseDeserializeEnd = System.nanoTime();
            if (responseCount != payload.size()) {
                throw new IllegalStateException("protobuf response mismatch");
            }

            return sample(
                    requestSerializeEnd - requestSerializeStart,
                    requestDeserializeEnd - requestDeserializeStart,
                    responseSerializeEnd - responseSerializeStart,
                    responseDeserializeEnd - responseDeserializeStart,
                    requestBytes.length,
                    responseBytes.length);
        };
    }

    private static BenchmarkRun createTelepactBenchmark(Scenario scenario) throws Exception {
        var schema = TelepactSchema.fromDirectory(Path.of("..", "schema", "telepact").toString());
        var clientSerializer = SerializerFactory.createClientSerializer();
        var serverSerializer = SerializerFactory.createServerSerializer(schema);
        var functionName = FUNCTION_NAMES.get(scenario.dataShape());

        return payload -> {
            var requestHeaders = new HashMap<String, Object>();
            if (!Objects.equals(scenario.method(), "telepact-json")) {
                requestHeaders.put("@binary_", true);
            }
            if (Objects.equals(scenario.method(), "telepact-packed-binary")) {
                requestHeaders.put("@pac_", true);
            }

            var requestMessage = new Message(requestHeaders, Map.of(functionName, Map.of("items", payload)));
            long requestSerializeStart = System.nanoTime();
            var requestBytes = clientSerializer.serialize(requestMessage);
            long requestSerializeEnd = System.nanoTime();
            long requestDeserializeStart = System.nanoTime();
            var requestRoundTrip = serverSerializer.deserialize(requestBytes);
            long requestDeserializeEnd = System.nanoTime();
            var requestItems = (List<?>) ((Map<String, Object>) requestRoundTrip.body.get(functionName)).get("items");
            if (requestItems.size() != payload.size()) {
                throw new IllegalStateException("telepact payload mismatch");
            }

            var responseHeaders = new HashMap<String, Object>();
            if (requestRoundTrip.headers.containsKey("@bin_")) {
                responseHeaders.put("@binary_", true);
                responseHeaders.put("@clientKnownBinaryChecksums_", requestRoundTrip.headers.get("@bin_"));
            }
            if (requestRoundTrip.headers.containsKey("@pac_")) {
                responseHeaders.put("@pac_", requestRoundTrip.headers.get("@pac_"));
            }
            var responseMessage = new Message(responseHeaders, Map.of("Ok_", Map.of("items", requestItems)));
            long responseSerializeStart = System.nanoTime();
            var responseBytes = serverSerializer.serialize(responseMessage);
            long responseSerializeEnd = System.nanoTime();
            long responseDeserializeStart = System.nanoTime();
            var responseRoundTrip = clientSerializer.deserialize(responseBytes);
            long responseDeserializeEnd = System.nanoTime();
            var responseItems = (List<?>) ((Map<String, Object>) responseRoundTrip.body.get("Ok_")).get("items");
            if (responseItems.size() != payload.size()) {
                throw new IllegalStateException("telepact response mismatch");
            }

            return sample(
                    requestSerializeEnd - requestSerializeStart,
                    requestDeserializeEnd - requestDeserializeStart,
                    responseSerializeEnd - responseSerializeStart,
                    responseDeserializeEnd - responseDeserializeStart,
                    requestBytes.length,
                    responseBytes.length);
        };
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

    private static List<String> parseCsv(String value, List<String> allowed) {
        if (value == null || value.isBlank()) {
            return allowed;
        }
        var selected = new ArrayList<String>();
        for (var part : value.split(",")) {
            if (!part.isBlank()) {
                selected.add(part);
            }
        }
        return selected.isEmpty() ? allowed : selected;
    }

    private static Map<String, Object> sample(long requestSerializationTimeNs, long requestDeserializationTimeNs,
            long responseSerializationTimeNs, long responseDeserializationTimeNs,
            long serializedRequestSizeBytes, long serializedResponseSizeBytes) {
        return Map.of(
                "requestSerializationTimeNs", requestSerializationTimeNs,
                "requestDeserializationTimeNs", requestDeserializationTimeNs,
                "responseSerializationTimeNs", responseSerializationTimeNs,
                "responseDeserializationTimeNs", responseDeserializationTimeNs,
                "serializedRequestSizeBytes", serializedRequestSizeBytes,
                "serializedResponseSizeBytes", serializedResponseSizeBytes);
    }

    private static Benchmark.TypicalRequest buildTypicalRequest(List<Map<String, Object>> payload) {
        var builder = Benchmark.TypicalRequest.newBuilder();
        for (var item : payload) {
            builder.addItems(Benchmark.TypicalItem.newBuilder()
                    .setAccountId(((Number) item.get("accountId")).longValue())
                    .setCustomerName((String) item.get("customerName"))
                    .setRegion((String) item.get("region"))
                    .setUnitPrice(((Number) item.get("unitPrice")).doubleValue())
                    .setQuantity(((Number) item.get("quantity")).longValue())
                    .build());
        }
        return builder.build();
    }

    private static Benchmark.StringsRequest buildStringsRequest(List<Map<String, Object>> payload) {
        var builder = Benchmark.StringsRequest.newBuilder();
        for (var item : payload) {
            builder.addItems(Benchmark.StringItem.newBuilder()
                    .setCode((String) item.get("code"))
                    .setCity((String) item.get("city"))
                    .setCountry((String) item.get("country"))
                    .setSegment((String) item.get("segment"))
                    .setStatus((String) item.get("status"))
                    .build());
        }
        return builder.build();
    }

    private static Benchmark.NumbersRequest buildNumbersRequest(List<Map<String, Object>> payload) {
        var builder = Benchmark.NumbersRequest.newBuilder();
        for (var item : payload) {
            builder.addItems(Benchmark.NumberItem.newBuilder()
                    .setAccountId(((Number) item.get("accountId")).longValue())
                    .setVisits(((Number) item.get("visits")).longValue())
                    .setScore(((Number) item.get("score")).doubleValue())
                    .setBalance(((Number) item.get("balance")).doubleValue())
                    .setRatio(((Number) item.get("ratio")).doubleValue())
                    .build());
        }
        return builder.build();
    }

    @FunctionalInterface
    private interface BenchmarkRun {
        Map<String, Object> run(List<Map<String, Object>> payload) throws Exception;
    }
}
