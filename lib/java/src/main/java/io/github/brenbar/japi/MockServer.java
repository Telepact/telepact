package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Random;

/**
 * A Mock instance of a jAPI server.
 * 
 * Clients can use this class as an alternative transport in their adapters to
 * interact with a functional jAPI with common mocking strategies.
 */
public class MockServer {

    public final Server processor;
    private final Random random;

    private final List<MockStub> stubs = new ArrayList<>();
    private final List<Invocation> invocations = new ArrayList<>();

    /**
     * Create a mock server with the given jAPI Schema.
     * 
     * @param jApiSchemaAsJson
     */
    public MockServer(String jApiSchemaAsJson) {
        var combinedSchemaJson = InternalParse.combineJsonSchemas(List.of(
                jApiSchemaAsJson,
                InternalMockJApi.JSON));
        this.processor = new Server(combinedSchemaJson, this::handle);
        this.random = new Random();
    }

    /**
     * Set an alternative RNG seed to be used for stub data generation.
     * 
     * @param seed
     * @return
     */
    public MockServer resetRandomSeed(Long seed) {
        this.random.setSeed(seed);
        return this;
    }

    /**
     * Process a given jAPI Request Message into a jAPI Response Message.
     * 
     * @param requestMessageBytes
     * @return
     */
    public byte[] process(byte[] message) {
        return this.processor.process(message);
    }

    private Map<String, Object> handle(Context context, Map<String, Object> argument) {
        context.requestHeaders.put("_mockJApiSchema", this.processor.jApiSchema);
        context.requestHeaders.put("_mockRandom", this.random);
        context.requestHeaders.put("_mockStubs", this.stubs);
        context.requestHeaders.put("_mockInvocations", this.invocations);
        return InternalMockServer.handle(context, argument);
    }

    /**
     * Create a function stub that will cause matching function calls to return the
     * result defined in the stub.
     * 
     * @param stub
     */
    public void createStub(MockStub stub) {
        var requestMessage = List.of(
                "fn._createStub",
                Map.of(),
                Map.ofEntries(
                        Map.entry("whenFunctionName", stub.whenFunctionName),
                        Map.entry("whenArgument", stub.whenArgument),
                        Map.entry("thenResult", stub.thenResult),
                        Map.entry("allowArgumentPartialMatch", stub.allowArgumentPartialMatch),
                        Map.entry("generateMissingResultFields", stub.generateMissingResultFields)));
        var requestMessageJson = this.processor.serializer.serialize(requestMessage);
        this.process(requestMessageJson);
    }

    /**
     * Verify an interaction occurred that matches the given verification criteria.
     * 
     * @param verification
     */
    public void verify(MockVerification verification) {
        Map<String, Object> verificationTimes;
        if (verification.verificationTimes instanceof MockVerification.UnlimitedNumberOfTimes u) {
            verificationTimes = Map.of("unlimited", Map.of());
        } else if (verification.verificationTimes instanceof MockVerification.ExactNumberOfTimes e) {
            verificationTimes = Map.of("exact", Map.of("times", e.times));
        } else if (verification.verificationTimes instanceof MockVerification.AtMostNumberOfTimes e) {
            verificationTimes = Map.of("atMost", Map.of("times", e.times));
        } else if (verification.verificationTimes instanceof MockVerification.AtLeastNumberOfTimes e) {
            verificationTimes = Map.of("atLeast", Map.of("times", e.times));
        } else {
            throw new JApiProcessError("Could not process verification times: %s"
                    .formatted(verification.verificationTimes.getClass().getName()));
        }

        var request = List.of(
                "fn._verify",
                Map.of(),
                Map.ofEntries(
                        Map.entry("verifyFunctionName", verification.functionName),
                        Map.entry("verifyArgument", verification.argument),
                        Map.entry("allowArgumentPartialMatch", verification.allowArgumentPartialMatch),
                        Map.entry("verificationTimes", verificationTimes)));

        var requestJson = this.processor.serializer.serialize(request);
        var responseJson = this.process(requestJson);
        var response = this.processor.serializer.deserialize(responseJson);
        var result = (Map<String, Object>) response.get(2);
        var err = (Map<String, Object>) result.get("err");
        if (err != null) {
            var errEntry = err.entrySet().stream().findAny().get();

            switch (errEntry.getKey()) {
                case "verificationFailure" -> {
                    var verificationFailureStruct = (Map<String, Object>) errEntry.getValue();
                    var details = verificationFailureStruct.get("details");
                    throw new AssertionError(details);
                }
            }
            throw new JApiProcessError("Could not process result: %s".formatted(result));
        }
    }

    /**
     * Verify that no interactions have occurred with this mock or that all
     * interactions have been verified.
     */
    public void verifyNoMoreInteractions() {
        var request = List.of(
                "fn._verifyNoMoreInteractions",
                Map.of(),
                Map.of());
        var requestJson = this.processor.serializer.serialize(request);
        var responseJson = this.process(requestJson);
        var response = this.processor.serializer.deserialize(responseJson);
        var result = (Map<String, Object>) response.get(2);
        var err = (Map<String, Object>) result.get("err");
        if (err != null) {
            var errEntry = err.entrySet().stream().findAny().get();

            switch (errEntry.getKey()) {
                case "verificationFailure" -> {
                    var verificationFailureStruct = (Map<String, Object>) errEntry.getValue();
                    var details = verificationFailureStruct.get("details");
                    throw new AssertionError(details);
                }
            }
            throw new JApiProcessError("Could not process result: %s".formatted(result));
        }
    }

    /**
     * Clear all interaction data.
     */
    public void clearInvocations() {
        var request = List.of(
                "fn._clearInvocations",
                Map.of(),
                Map.of());
        var requestJson = this.processor.serializer.serialize(request);
        var responseJson = this.process(requestJson);
        var response = this.processor.serializer.deserialize(responseJson);
        var result = (Map<String, Object>) response.get(2);
        var err = (Map<String, Object>) result.get("err");
        if (err != null) {
            throw new JApiProcessError("Could not process result: %s".formatted(result));
        }
    }

    /**
     * Clear all stub conditions.
     */
    public void clearStubs() {
        var request = List.of(
                "fn._clearStubs",
                Map.of(),
                Map.of());
        var requestJson = this.processor.serializer.serialize(request);
        var responseJson = this.process(requestJson);
        var response = this.processor.serializer.deserialize(responseJson);
        var result = (Map<String, Object>) response.get(2);
        var err = (Map<String, Object>) result.get("err");
        if (err != null) {
            throw new JApiProcessError("Could not process result: %s".formatted(result));
        }
    }
}
