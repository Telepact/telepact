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

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.github.telepact.Client;
import io.github.telepact.FunctionRouter;
import io.github.telepact.Message;
import io.github.telepact.Serializer;
import io.github.telepact.Server;
import io.github.telepact.TelepactSchema;
import io.github.telepact.TelepactSchemaFiles;
import io.github.telepact.performance.proto.BenchmarkProto.NumberItem;
import io.github.telepact.performance.proto.BenchmarkProto.NumberList;
import io.github.telepact.performance.proto.BenchmarkProto.Payload;
import io.github.telepact.performance.proto.BenchmarkProto.RoundTripRequest;
import io.github.telepact.performance.proto.BenchmarkProto.RoundTripResponse;
import io.github.telepact.performance.proto.BenchmarkProto.StringItem;
import io.github.telepact.performance.proto.BenchmarkProto.StringList;
import io.github.telepact.performance.proto.BenchmarkProto.TypicalItem;
import io.github.telepact.performance.proto.BenchmarkProto.TypicalList;
import io.nats.client.Connection;
import io.nats.client.Dispatcher;
import io.nats.client.MessageHandler;
import io.nats.client.Nats;
import io.nats.client.Options;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.TreeMap;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.atomic.AtomicReference;

public final class BenchmarkWorker {
    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

    private record ParsedArgs(String language, String latency, String natsUrl, String schemaDir, String manifest, String output) {}

    private static long nowNs() {
        return System.nanoTime();
    }

    private static Server buildTelepactServer(String schemaDir, AtomicReference<Map<String, Object>> currentSample) {
        var files = new TelepactSchemaFiles(schemaDir);
        var schema = TelepactSchema.fromFileJsonMap(files.filenamesToJson);
        var options = new Server.Options();
        options.authRequired = false;
        options.onRequest = (_message) -> {
            var sample = currentSample.get();
            if (sample != null) {
                var received = ((Number) sample.get("server_request_received_ns")).longValue();
                sample.put("server_request_deserialize_ns", nowNs() - received);
            }
        };
        options.onResponse = (_message) -> {
            var sample = currentSample.get();
            if (sample != null) {
                sample.put("server_response_ready_ns", nowNs());
            }
        };
        var functionRouter = new FunctionRouter(Map.of(
                "fn.roundTrip",
                (io.github.telepact.FunctionRoute) (requestMessage) -> new Message(Map.of(), Map.of("Ok_", requestMessage.body.get("fn.roundTrip")))));
        return new Server(schema, functionRouter, options);
    }

    private static Payload payloadToProto(Map<String, Object> payloadMap) {
        var entry = payloadMap.entrySet().iterator().next();
        var builder = Payload.newBuilder();
        switch (entry.getKey()) {
            case "TypicalSingle" -> builder.setTypicalSingle(typicalItem((Map<String, Object>) entry.getValue()));
            case "TypicalList" -> builder.setTypicalList(typicalList((Map<String, Object>) entry.getValue()));
            case "StringSingle" -> builder.setStringSingle(stringItem((Map<String, Object>) entry.getValue()));
            case "StringList" -> builder.setStringList(stringList((Map<String, Object>) entry.getValue()));
            case "NumberSingle" -> builder.setNumberSingle(numberItem((Map<String, Object>) entry.getValue()));
            case "NumberList" -> builder.setNumberList(numberList((Map<String, Object>) entry.getValue()));
            default -> throw new IllegalArgumentException("unknown payload variant: " + entry.getKey());
        }
        return builder.build();
    }

    private static TypicalItem typicalItem(Map<String, Object> value) {
        return TypicalItem.newBuilder()
                .setPrimaryId((String) value.get("primaryId"))
                .setSecondaryId((String) value.get("secondaryId"))
                .setCount(((Number) value.get("count")).intValue())
                .setRatio(((Number) value.get("ratio")).doubleValue())
                .build();
    }

    private static TypicalList typicalList(Map<String, Object> value) {
        var builder = TypicalList.newBuilder();
        for (var item : (List<Map<String, Object>>) value.get("items")) {
            builder.addItems(typicalItem(item));
        }
        return builder.build();
    }

    private static StringItem stringItem(Map<String, Object> value) {
        return StringItem.newBuilder()
                .setAlpha((String) value.get("alpha"))
                .setBeta((String) value.get("beta"))
                .setGamma((String) value.get("gamma"))
                .setDelta((String) value.get("delta"))
                .build();
    }

    private static StringList stringList(Map<String, Object> value) {
        var builder = StringList.newBuilder();
        for (var item : (List<Map<String, Object>>) value.get("items")) {
            builder.addItems(stringItem(item));
        }
        return builder.build();
    }

    private static NumberItem numberItem(Map<String, Object> value) {
        return NumberItem.newBuilder()
                .setLeft(((Number) value.get("left")).intValue())
                .setRight(((Number) value.get("right")).intValue())
                .setRatio(((Number) value.get("ratio")).doubleValue())
                .setOffset(((Number) value.get("offset")).doubleValue())
                .build();
    }

    private static NumberList numberList(Map<String, Object> value) {
        var builder = NumberList.newBuilder();
        for (var item : (List<Map<String, Object>>) value.get("items")) {
            builder.addItems(numberItem(item));
        }
        return builder.build();
    }

    private static Map<String, Object> payloadFromProto(Payload payload) {
        return switch (payload.getValueCase()) {
            case TYPICAL_SINGLE -> Map.of("TypicalSingle", Map.of(
                    "primaryId", payload.getTypicalSingle().getPrimaryId(),
                    "secondaryId", payload.getTypicalSingle().getSecondaryId(),
                    "count", payload.getTypicalSingle().getCount(),
                    "ratio", payload.getTypicalSingle().getRatio()));
            case TYPICAL_LIST -> Map.of("TypicalList", Map.of("items", payload.getTypicalList().getItemsList().stream().map(item -> Map.of(
                    "primaryId", item.getPrimaryId(),
                    "secondaryId", item.getSecondaryId(),
                    "count", item.getCount(),
                    "ratio", item.getRatio())).toList()));
            case STRING_SINGLE -> Map.of("StringSingle", Map.of(
                    "alpha", payload.getStringSingle().getAlpha(),
                    "beta", payload.getStringSingle().getBeta(),
                    "gamma", payload.getStringSingle().getGamma(),
                    "delta", payload.getStringSingle().getDelta()));
            case STRING_LIST -> Map.of("StringList", Map.of("items", payload.getStringList().getItemsList().stream().map(item -> Map.of(
                    "alpha", item.getAlpha(),
                    "beta", item.getBeta(),
                    "gamma", item.getGamma(),
                    "delta", item.getDelta())).toList()));
            case NUMBER_SINGLE -> Map.of("NumberSingle", Map.of(
                    "left", payload.getNumberSingle().getLeft(),
                    "right", payload.getNumberSingle().getRight(),
                    "ratio", payload.getNumberSingle().getRatio(),
                    "offset", payload.getNumberSingle().getOffset()));
            case NUMBER_LIST -> Map.of("NumberList", Map.of("items", payload.getNumberList().getItemsList().stream().map(item -> Map.of(
                    "left", item.getLeft(),
                    "right", item.getRight(),
                    "ratio", item.getRatio(),
                    "offset", item.getOffset())).toList()));
            case VALUE_NOT_SET -> throw new IllegalArgumentException("payload missing value");
        };
    }

    private static byte[] encodeProtoRequest(Map<String, Object> request) {
        return RoundTripRequest.newBuilder()
                .setScenario((String) request.get("scenario"))
                .setPayload(payloadToProto((Map<String, Object>) request.get("payload")))
                .build()
                .toByteArray();
    }

    private static Map<String, Object> decodeProtoRequest(byte[] payload) throws Exception {
        var request = RoundTripRequest.parseFrom(payload);
        return Map.of("scenario", request.getScenario(), "payload", payloadFromProto(request.getPayload()));
    }

    private static byte[] encodeProtoResponse(Map<String, Object> response) {
        return RoundTripResponse.newBuilder()
                .setScenario((String) response.get("scenario"))
                .setPayload(payloadToProto((Map<String, Object>) response.get("payload")))
                .build()
                .toByteArray();
    }

    private static Map<String, Object> decodeProtoResponse(byte[] payload) throws Exception {
        var response = RoundTripResponse.parseFrom(payload);
        return Map.of("scenario", response.getScenario(), "payload", payloadFromProto(response.getPayload()));
    }

    private static final class TelepactBenchClient {
        private final Client client;
        private final Connection connection;
        private final String subject;
        private final boolean packed;
        private final AtomicReference<Map<String, Object>> currentSample;

        private TelepactBenchClient(Connection connection, String subject, boolean useBinary, boolean packed,
                AtomicReference<Map<String, Object>> currentSample) {
            this.connection = connection;
            this.subject = subject;
            this.packed = packed;
            this.currentSample = currentSample;
            var options = new Client.Options();
            options.useBinary = useBinary;
            options.alwaysSendJson = !useBinary;
            this.client = new Client((message, serializer) -> CompletableFuture.supplyAsync(() -> {
                try {
                    var sample = Objects.requireNonNull(this.currentSample.get());
                    var serializeStart = nowNs();
                    var requestBytes = serializer.serialize(message);
                    sample.put("client_request_serialize_ns", nowNs() - serializeStart);
                    sample.put("request_size_bytes", requestBytes.length);
                    sample.put("client_request_sent_ns", nowNs());
                    var response = connection.request(subject, requestBytes, Duration.ofSeconds(30));
                    sample.put("client_response_received_ns", nowNs());
                    var responseBytes = response.getData();
                    sample.put("response_size_bytes", responseBytes.length);
                    var deserializeStart = nowNs();
                    var decoded = serializer.deserialize(responseBytes);
                    sample.put("client_response_deserialize_ns", nowNs() - deserializeStart);
                    sample.put("request_network_transit_ns", ((Number) sample.get("server_request_received_ns")).longValue() - ((Number) sample.get("client_request_sent_ns")).longValue());
                    sample.put("response_network_transit_ns", ((Number) sample.get("client_response_received_ns")).longValue() - ((Number) sample.get("server_response_sent_ns")).longValue());
                    return decoded;
                } catch (Exception e) {
                    throw new RuntimeException(e);
                }
            }), options);
        }

        private void roundTrip(Map<String, Object> request, Map<String, Object> sample) {
            currentSample.set(sample);
            try {
                var headers = new HashMap<String, Object>();
                if (packed) {
                    headers.put("@pac_", true);
                }
                var response = client.request(new Message(headers, Map.of("fn.roundTrip", request)));
                if (!Objects.equals(response.body.get("Ok_"), request)) {
                    throw new IllegalStateException("telepact response mismatch");
                }
            } finally {
                currentSample.set(null);
            }
        }
    }

    private static Map<String, Object> runPlainJson(Connection connection, String subject, Map<String, Object> request,
            Map<String, Object> sample, AtomicReference<Map<String, Object>> currentSample) throws Exception {
        currentSample.set(sample);
        try {
            var serializeStart = nowNs();
            var requestBytes = OBJECT_MAPPER.writeValueAsBytes(request);
            sample.put("client_request_serialize_ns", nowNs() - serializeStart);
            sample.put("request_size_bytes", requestBytes.length);
            sample.put("client_request_sent_ns", nowNs());
            var response = connection.request(subject, requestBytes, Duration.ofSeconds(30));
            sample.put("client_response_received_ns", nowNs());
            var responseBytes = response.getData();
            sample.put("response_size_bytes", responseBytes.length);
            var deserializeStart = nowNs();
            var decoded = OBJECT_MAPPER.readValue(responseBytes, new TypeReference<Map<String, Object>>() {});
            sample.put("client_response_deserialize_ns", nowNs() - deserializeStart);
            sample.put("request_network_transit_ns", ((Number) sample.get("server_request_received_ns")).longValue() - ((Number) sample.get("client_request_sent_ns")).longValue());
            sample.put("response_network_transit_ns", ((Number) sample.get("client_response_received_ns")).longValue() - ((Number) sample.get("server_response_sent_ns")).longValue());
            return decoded;
        } finally {
            currentSample.set(null);
        }
    }

    private static Map<String, Object> runProtobuf(Connection connection, String subject, Map<String, Object> request,
            Map<String, Object> sample, AtomicReference<Map<String, Object>> currentSample) throws Exception {
        currentSample.set(sample);
        try {
            var serializeStart = nowNs();
            var requestBytes = encodeProtoRequest(request);
            sample.put("client_request_serialize_ns", nowNs() - serializeStart);
            sample.put("request_size_bytes", requestBytes.length);
            sample.put("client_request_sent_ns", nowNs());
            var response = connection.request(subject, requestBytes, Duration.ofSeconds(30));
            sample.put("client_response_received_ns", nowNs());
            var responseBytes = response.getData();
            sample.put("response_size_bytes", responseBytes.length);
            var deserializeStart = nowNs();
            var decoded = decodeProtoResponse(responseBytes);
            sample.put("client_response_deserialize_ns", nowNs() - deserializeStart);
            sample.put("request_network_transit_ns", ((Number) sample.get("server_request_received_ns")).longValue() - ((Number) sample.get("client_request_sent_ns")).longValue());
            sample.put("response_network_transit_ns", ((Number) sample.get("client_response_received_ns")).longValue() - ((Number) sample.get("server_response_sent_ns")).longValue());
            return decoded;
        } finally {
            currentSample.set(null);
        }
    }

    private static ParsedArgs parseArgs(String[] args) {
        var parsed = new TreeMap<String, String>();
        for (var i = 0; i < args.length - 1; i += 2) {
            parsed.put(args[i], args[i + 1]);
        }
        return new ParsedArgs(
                parsed.getOrDefault("--language", "java"),
                parsed.get("--latency"),
                parsed.get("--nats-url"),
                parsed.get("--schema-dir"),
                parsed.get("--manifest"),
                parsed.get("--output"));
    }

    public static void main(String[] args) throws Exception {
        var parsed = parseArgs(args);
        var manifest = OBJECT_MAPPER.readValue(new java.io.File(parsed.manifest), new TypeReference<Map<String, Object>>() {});
        var currentSample = new AtomicReference<Map<String, Object>>();
        var connection = Nats.connect(new Options.Builder().server(parsed.natsUrl).build());

        var subjectPrefix = "telepact.performance." + parsed.language + "." + parsed.latency + "." + Long.toHexString(System.nanoTime());
        var telepactJsonSubject = subjectPrefix + ".telepact-json";
        var telepactBinarySubject = subjectPrefix + ".telepact-binary";
        var telepactPackedSubject = subjectPrefix + ".telepact-packed";
        var protobufSubject = subjectPrefix + ".protobuf";
        var jsonSubject = subjectPrefix + ".json";

        var server = buildTelepactServer(parsed.schemaDir, currentSample);
        MessageHandler telepactHandler = msg -> {
            try {
                var sample = currentSample.get();
                if (sample == null) {
                    throw new IllegalStateException("missing active sample");
                }
                sample.put("server_request_received_ns", nowNs());
                var response = server.process(msg.getData());
                sample.put("server_response_serialize_ns", nowNs() - ((Number) sample.get("server_response_ready_ns")).longValue());
                sample.put("server_response_sent_ns", nowNs());
                connection.publish(msg.getReplyTo(), response.bytes);
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        };
        MessageHandler protobufHandler = msg -> {
            try {
                var sample = currentSample.get();
                if (sample == null) {
                    throw new IllegalStateException("missing active sample");
                }
                sample.put("server_request_received_ns", nowNs());
                var deserializeStart = nowNs();
                var request = decodeProtoRequest(msg.getData());
                sample.put("server_request_deserialize_ns", nowNs() - deserializeStart);
                var serializeStart = nowNs();
                var responseBytes = encodeProtoResponse(request);
                sample.put("server_response_serialize_ns", nowNs() - serializeStart);
                sample.put("server_response_sent_ns", nowNs());
                connection.publish(msg.getReplyTo(), responseBytes);
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        };
        MessageHandler jsonHandler = msg -> {
            try {
                var sample = currentSample.get();
                if (sample == null) {
                    throw new IllegalStateException("missing active sample");
                }
                sample.put("server_request_received_ns", nowNs());
                var deserializeStart = nowNs();
                var request = OBJECT_MAPPER.readValue(msg.getData(), new TypeReference<Map<String, Object>>() {});
                sample.put("server_request_deserialize_ns", nowNs() - deserializeStart);
                var serializeStart = nowNs();
                var responseBytes = OBJECT_MAPPER.writeValueAsBytes(request);
                sample.put("server_response_serialize_ns", nowNs() - serializeStart);
                sample.put("server_response_sent_ns", nowNs());
                connection.publish(msg.getReplyTo(), responseBytes);
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        };

        List<Dispatcher> dispatchers = List.of(
                connection.createDispatcher(telepactHandler),
                connection.createDispatcher(telepactHandler),
                connection.createDispatcher(telepactHandler),
                connection.createDispatcher(protobufHandler),
                connection.createDispatcher(jsonHandler));
        dispatchers.get(0).subscribe(telepactJsonSubject);
        dispatchers.get(1).subscribe(telepactBinarySubject);
        dispatchers.get(2).subscribe(telepactPackedSubject);
        dispatchers.get(3).subscribe(protobufSubject);
        dispatchers.get(4).subscribe(jsonSubject);
        connection.flush(Duration.ofSeconds(5));

        var telepactJsonClient = new TelepactBenchClient(connection, telepactJsonSubject, false, false, currentSample);
        var telepactBinaryClient = new TelepactBenchClient(connection, telepactBinarySubject, true, false, currentSample);
        var telepactPackedClient = new TelepactBenchClient(connection, telepactPackedSubject, true, true, currentSample);

        var scenarios = (List<Map<String, Object>>) manifest.get("scenarios");
        var methods = (List<String>) manifest.get("methods");
        var warmupIterations = ((Number) manifest.get("warmupIterations")).intValue();
        var measureIterations = ((Number) manifest.get("measureIterations")).intValue();
        var samples = new ArrayList<Map<String, Object>>();

        for (var scenario : scenarios) {
            var request = (Map<String, Object>) scenario.get("request");
            var response = (Map<String, Object>) scenario.get("response");
            for (var warmup = 0; warmup < warmupIterations; warmup += 1) {
                telepactJsonClient.roundTrip(request, new HashMap<>());
                telepactBinaryClient.roundTrip(request, new HashMap<>());
                telepactPackedClient.roundTrip(request, new HashMap<>());
                if (!Objects.equals(runProtobuf(connection, protobufSubject, request, new HashMap<>(), currentSample), response)) {
                    throw new IllegalStateException("protobuf warmup mismatch");
                }
                if (!Objects.equals(runPlainJson(connection, jsonSubject, request, new HashMap<>(), currentSample), response)) {
                    throw new IllegalStateException("json warmup mismatch");
                }
            }
            for (var method : methods) {
                for (var iteration = 0; iteration < measureIterations; iteration += 1) {
                    var sample = new HashMap<String, Object>();
                    sample.put("language", parsed.language);
                    sample.put("latency", parsed.latency);
                    sample.put("method", method);
                    sample.put("scenario", scenario.get("name"));
                    sample.put("collection_shape", scenario.get("collectionShape"));
                    sample.put("data_shape", scenario.get("dataShape"));
                    sample.put("iteration", iteration);
                    switch (method) {
                        case "telepact_json" -> telepactJsonClient.roundTrip(request, sample);
                        case "telepact_binary" -> telepactBinaryClient.roundTrip(request, sample);
                        case "telepact_packed_binary" -> telepactPackedClient.roundTrip(request, sample);
                        case "protobuf" -> {
                            if (!Objects.equals(runProtobuf(connection, protobufSubject, request, sample, currentSample), response)) {
                                throw new IllegalStateException("protobuf mismatch");
                            }
                        }
                        default -> {
                            if (!Objects.equals(runPlainJson(connection, jsonSubject, request, sample, currentSample), response)) {
                                throw new IllegalStateException("json mismatch");
                            }
                        }
                    }
                    samples.add(sample);
                }
            }
        }

        OBJECT_MAPPER.writerWithDefaultPrettyPrinter().writeValue(new java.io.File(parsed.output), samples);
        connection.drain(Duration.ofSeconds(5));
    }
}
