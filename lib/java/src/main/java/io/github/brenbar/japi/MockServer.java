package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.function.Consumer;

/**
 * A Mock instance of a jAPI server.
 * 
 * Clients can use this class as an alternative transport in their adapters to
 * interact with a functional jAPI with common mocking strategies.
 */
public class MockServer {

    public final Server server;
    private final Random random;
    private boolean enableGeneratedDefaultStub;

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
        this.server = new Server(combinedSchemaJson, this::handle);
        this.random = new Random();
        this.enableGeneratedDefaultStub = true;
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
     * Set an error handler to run on every error that occurs during request
     * processing.
     * 
     * @param onError
     * @return
     */
    public MockServer setOnError(Consumer<Throwable> onError) {
        this.server.onError = onError;
        return this;
    }

    public MockServer setEnableGeneratedDefaultStub(boolean enableGeneratedDefaultStub) {
        this.enableGeneratedDefaultStub = enableGeneratedDefaultStub;
        return this;
    }

    /**
     * Process a given jAPI Request Message into a jAPI Response Message.
     * 
     * @param requestMessageBytes
     * @return
     */
    public byte[] process(byte[] message) {
        return this.server.process(message);
    }

    private Map<String, Object> handle(Context context, Map<String, Object> argument) {
        context.requestHeaders.put("_mockJApiSchema", this.server.jApiSchema);
        context.requestHeaders.put("_mockRandom", this.random);
        context.requestHeaders.put("_mockStubs", this.stubs);
        context.requestHeaders.put("_mockInvocations", this.invocations);
        context.requestHeaders.put("_mockEnableGeneratedDefaultStub", this.enableGeneratedDefaultStub);
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
                        Map.entry("strictMatch", !stub.allowArgumentPartialMatch),
                        Map.entry("generateMissingResultFields", stub.generateMissingResultFields)));
        var requestMessageJson = this.server.serializer.serialize(requestMessage);
        var responseJson = this.process(requestMessageJson);
        var response = this.server.serializer.deserialize(responseJson);
        var result = (Map<String, Object>) response.get(2);
        var err = (Map<String, Object>) result.get("err");
        if (err != null) {
            throw new JApiProcessError(String.valueOf(result));
        }
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
                        Map.entry("verifyTimes", verificationTimes),
                        Map.entry("strictMatch", !verification.allowArgumentPartialMatch)));

        var requestJson = this.server.serializer.serialize(request);
        var responseJson = this.process(requestJson);
        var response = this.server.serializer.deserialize(responseJson);
        var result = (Map<String, Object>) response.get(2);
        var err = (Map<String, Object>) result.get("err");
        if (err != null) {
            var errEntry = err.entrySet().stream().findAny().get();

            switch (errEntry.getKey()) {
                case "_verificationFailure" -> {
                    var verificationFailureStruct = (Map<String, Object>) errEntry.getValue();
                    var details = verificationFailureStruct.get("details");
                    throw new AssertionError(details);
                }
            }
            throw new JApiProcessError(String.valueOf(result));
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
        var requestJson = this.server.serializer.serialize(request);
        var responseJson = this.process(requestJson);
        var response = this.server.serializer.deserialize(responseJson);
        var result = (Map<String, Object>) response.get(2);
        var err = (Map<String, Object>) result.get("err");
        if (err != null) {
            var errEntry = err.entrySet().stream().findAny().get();

            switch (errEntry.getKey()) {
                case "_verificationFailure" -> {
                    var verificationFailureStruct = (Map<String, Object>) errEntry.getValue();
                    var details = verificationFailureStruct.get("details");
                    throw new AssertionError(details);
                }
            }
            throw new JApiProcessError(String.valueOf(result));
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
        var requestJson = this.server.serializer.serialize(request);
        var responseJson = this.process(requestJson);
        var response = this.server.serializer.deserialize(responseJson);
        var result = (Map<String, Object>) response.get(2);
        var err = (Map<String, Object>) result.get("err");
        if (err != null) {
            throw new JApiProcessError(String.valueOf(result));
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
        var requestJson = this.server.serializer.serialize(request);
        var responseJson = this.process(requestJson);
        var response = this.server.serializer.deserialize(responseJson);
        var result = (Map<String, Object>) response.get(2);
        var err = (Map<String, Object>) result.get("err");
        if (err != null) {
            throw new JApiProcessError(String.valueOf(result));
        }
    }
}
