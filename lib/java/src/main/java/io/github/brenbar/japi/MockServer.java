package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Random;
import java.util.function.Function;

/**
 * A Mock instance of a jAPI server.
 * 
 * Clients can use this class as an alternative transport in their adapters to
 * interact with a functional jAPI with common mocking strategies.
 */
public class MockServer {

    public final Server processor;
    private final Random random;

    private final List<Mock> mocks = new ArrayList<>();
    private final List<Invocation> invocations = new ArrayList<>();

    /**
     * Applies a criteria to the number of times a verification should be matched.
     */
    public interface VerificationTimes {

    }

    /**
     * Allows any number of matches for a verification query.
     */
    public static class UnlimitedNumberOfTimes implements VerificationTimes {

    }

    /**
     * Allows only the given number of matches for a verification query.
     */
    public static class ExactNumberOfTimes implements VerificationTimes {
        public final int times;

        public ExactNumberOfTimes(int times) {
            this.times = times;
        }
    }

    /**
     * Create a mock server with the given jAPI Schema.
     * 
     * @param jApiSchemaAsJson
     */
    public MockServer(String jApiSchemaAsJson) {
        this.processor = new Server(jApiSchemaAsJson, this::handle);
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

    private Map<String, Object> handle(Context context, Map<String, Object> input) {
        return InternalMockProcess.handle(context, input, this.processor.jApiSchema, this.random, this.mocks,
                this.invocations);
    }

    /**
     * Create a mock condition when the given function name matches and the given
     * input partially matches.
     * 
     * @param whenFunctionName
     * @param whenPartialMatchInput
     * @param thenAnswerOutput
     */
    public void mockPartial(String whenFunctionName, Map<String, Object> whenPartialMatchInput,
            Function<Map<String, Object>, Map<String, Object>> thenAnswerOutput) {
        mocks.add(0, new Mock(whenFunctionName, whenPartialMatchInput, false, thenAnswerOutput));
    }

    /**
     * Create a mock condition when the given function name matches and the given
     * input exactly matches.
     * 
     * @param whenFunctionName
     * @param whenExactMatchInput
     * @param thenAnswerOutput
     */
    public void mockExact(String whenFunctionName, Map<String, Object> whenExactMatchInput,
            Function<Map<String, Object>, Map<String, Object>> thenAnswerOutput) {
        mocks.add(0, new Mock(whenFunctionName, whenExactMatchInput, true, thenAnswerOutput));
    }

    /**
     * Verify an interaction occurred that both matches the given function name and
     * partially matches the given input.
     * 
     * @param functionName
     * @param partialMatchInput
     */
    public void verifyPartial(String functionName, Map<String, Object> partialMatchInput) {
        verifyPartial(functionName, partialMatchInput, new UnlimitedNumberOfTimes());
    }

    /**
     * Verify an interaction occurred the given number of times that both matches
     * the given function name and partially matches the given input.
     * 
     * @param functionName
     * @param partialMatchInput
     * @param verificationTimes
     */
    public void verifyPartial(String functionName, Map<String, Object> partialMatchInput,
            VerificationTimes verificationTimes) {
        var matchesFound = 0;
        for (var invocation : invocations) {
            if (Objects.equals(invocation.functionName, functionName)) {
                if (InternalMockProcess.isSubMap(invocation.functionInput, partialMatchInput)) {
                    invocation.verified = true;
                    matchesFound += 1;
                }
            }
        }

        if (verificationTimes instanceof ExactNumberOfTimes e) {
            if (e.times != matchesFound) {
                var errorString = new StringBuilder("""
                        Wanted exactly %d partial matches, but found %d.
                        Query:
                        %s(%s)
                        """.formatted(e.times, matchesFound, functionName, partialMatchInput));
                throw new AssertionError(errorString);
            }
        }

        if (matchesFound > 0) {
            return;
        }

        var errorString = new StringBuilder("""
                No matching invocations.
                Wanted partial match:
                %s(%s)
                Available:
                """.formatted(functionName, partialMatchInput));
        var functionInvocations = invocations.stream().filter(i -> Objects.equals(functionName, i.functionName))
                .toList();
        if (functionInvocations.isEmpty()) {
            errorString.append("<none>");
        } else {
            for (var invocation : functionInvocations) {
                errorString.append("%s(%s)\n".formatted(invocation.functionName, invocation.functionInput));
            }
        }
        throw new AssertionError(errorString);
    }

    /**
     * Verify an interaction occurred that both matches the given function name and
     * exactly matches the given input.
     * 
     * @param functionName
     * @param exactMatchInput
     */
    public void verifyExact(String functionName, Map<String, Object> exactMatchInput) {
        verifyExact(functionName, exactMatchInput, new UnlimitedNumberOfTimes());
    }

    /**
     * Verify an interaction occurred the given number of times that both matches
     * the given function name and exactly matches the given input.
     * 
     * @param functionName
     * @param exactMatchFunctionInput
     * @param verificationTimes
     */
    public void verifyExact(String functionName, Map<String, Object> exactMatchFunctionInput,
            VerificationTimes verificationTimes) {
        var matchesFound = 0;
        for (var invocation : invocations) {
            if (Objects.equals(invocation.functionName, functionName)) {
                if (Objects.equals(invocation.functionInput, exactMatchFunctionInput)) {
                    invocation.verified = true;
                    matchesFound += 1;
                }
            }
        }

        if (verificationTimes instanceof ExactNumberOfTimes e) {
            if (e.times != matchesFound) {
                var errorString = new StringBuilder("""
                        Wanted exactly %d exact matches, but found %d.
                        Query:
                        %s(%s)
                        """.formatted(e.times, matchesFound, functionName, exactMatchFunctionInput));
                throw new AssertionError(errorString);
            }
        }

        if (matchesFound > 0) {
            return;
        }

        var errorString = new StringBuilder("""
                No matching invocations.
                Wanted exact match:
                %s(%s)
                Available:
                """.formatted(functionName, exactMatchFunctionInput));
        var functionInvocations = invocations.stream().filter(i -> Objects.equals(functionName, i.functionName))
                .toList();
        if (functionInvocations.isEmpty()) {
            errorString.append("<none>");
        } else {
            for (var invocation : functionInvocations) {
                errorString.append("%s(%s)\n".formatted(invocation.functionName, invocation.functionInput));
            }
        }
        throw new AssertionError(errorString);
    }

    /**
     * Verify no more interactions occurred with this mock.
     * 
     * (This function implies that no interactions occurred or that all interactions
     * up to this point have already been verified.)
     */
    public void verifyNoMoreInteractions() {
        var invocationsNotVerified = this.invocations.stream().filter(i -> !i.verified).toList();

        if (invocationsNotVerified.size() > 0) {
            var errorString = new StringBuilder("""
                    Expected no more interactions, but more were found.
                    Available:
                    """);
            for (var invocation : invocationsNotVerified) {
                errorString.append("%s(%s)\n".formatted(invocation.functionName, invocation.functionInput));
            }
            throw new AssertionError(errorString);
        }
    }

    /**
     * Clear all interaction data.
     */
    public void clearInvocations() {
        this.invocations.clear();
    }

    /**
     * Clear all mock conditions.
     */
    public void clearMocks() {
        this.mocks.clear();
    }
}
