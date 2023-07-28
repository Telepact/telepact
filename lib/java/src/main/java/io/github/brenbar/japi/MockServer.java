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

    private Map<String, Object> handle(Context context, Map<String, Object> argument) {
        return InternalMockServer.handle(context, argument, this.processor.jApiSchema, this.random, this.mocks,
                this.invocations);
    }

    /**
     * Create a mock condition when the given function name matches and the given
     * argument partially matches.
     * 
     * @param whenFunctionName
     * @param whenPartialMatchArgument
     * @param thenAnswerResult
     */
    public void mockPartial(String whenFunctionName, Map<String, Object> whenPartialMatchArgument,
            Function<Map<String, Object>, Map<String, Object>> thenAnswerResult) {
        mocks.add(0, new Mock(whenFunctionName, whenPartialMatchArgument, false, thenAnswerResult));
    }

    /**
     * Create a mock condition when the given function name matches and the given
     * argument exactly matches.
     * 
     * @param whenFunctionName
     * @param whenExactMatchArgument
     * @param thenAnswerResult
     */
    public void mockExact(String whenFunctionName, Map<String, Object> whenExactMatchArgument,
            Function<Map<String, Object>, Map<String, Object>> thenAnswerResult) {
        mocks.add(0, new Mock(whenFunctionName, whenExactMatchArgument, true, thenAnswerResult));
    }

    /**
     * Verify an interaction occurred that both matches the given function name and
     * partially matches the given argument.
     * 
     * @param functionName
     * @param partialMatchArgument
     */
    public void verifyPartial(String functionName, Map<String, Object> partialMatchArgument) {
        verifyPartial(functionName, partialMatchArgument, new UnlimitedNumberOfTimes());
    }

    /**
     * Verify an interaction occurred the given number of times that both matches
     * the given function name and partially matches the given argument.
     * 
     * @param functionName
     * @param partialMatchArgument
     * @param verificationTimes
     */
    public void verifyPartial(String functionName, Map<String, Object> partialMatchArgument,
            VerificationTimes verificationTimes) {
        InternalMockServer.verifyPartial(functionName, partialMatchArgument, verificationTimes, this.invocations);
    }

    /**
     * Verify an interaction occurred that both matches the given function name and
     * exactly matches the given argument.
     * 
     * @param functionName
     * @param exactMatchArgument
     */
    public void verifyExact(String functionName, Map<String, Object> exactMatchArgument) {
        verifyExact(functionName, exactMatchArgument, new UnlimitedNumberOfTimes());
    }

    /**
     * Verify an interaction occurred the given number of times that both matches
     * the given function name and exactly matches the given argument.
     * 
     * @param functionName
     * @param exactMatchFunctionArgument
     * @param verificationTimes
     */
    public void verifyExact(String functionName, Map<String, Object> exactMatchFunctionArgument,
            VerificationTimes verificationTimes) {
        InternalMockServer.verifyExact(functionName, exactMatchFunctionArgument, verificationTimes, this.invocations);
    }

    /**
     * Verify no more interactions occurred with this mock.
     * 
     * (This function implies that no interactions occurred or that all interactions
     * up to this point have already been verified.)
     */
    public void verifyNoMoreInteractions() {
        InternalMockServer.verifyNoMoreInteractions(this.invocations);
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
