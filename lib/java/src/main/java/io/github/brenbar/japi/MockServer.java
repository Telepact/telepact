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

    interface VerificationTimes {

    }

    public static class UnlimitedNumberOfTimes implements VerificationTimes {

    }

    public static class ExactNumberOfTimes implements VerificationTimes {
        public final int times;

        public ExactNumberOfTimes(int times) {
            this.times = times;
        }
    }

    public MockServer(String jApi) {
        this.processor = new Server(jApi, this::handle);
        this.random = new Random();
    }

    public MockServer resetRandomSeed(Long seed) {
        this.random.setSeed(seed);
        return this;
    }

    public byte[] process(byte[] message) {
        return this.processor.process(message);
    }

    private Map<String, Object> handle(Context context, Map<String, Object> input) {
        return InternalMockProcess.handle(context, input, this.processor.jApiSchema, this.random, this.mocks,
                this.invocations);
    }

    public void mockPartial(String whenFunctionName, Map<String, Object> whenPartialMatchFunctionInput,
            Function<Map<String, Object>, Map<String, Object>> thenAnswerFunctionOutput) {
        mocks.add(0, new Mock(whenFunctionName, whenPartialMatchFunctionInput, false, thenAnswerFunctionOutput));
    }

    public void mockExact(String whenFunctionName, Map<String, Object> whenExactMatchFunctionInput,
            Function<Map<String, Object>, Map<String, Object>> thenAnswerOutput) {
        mocks.add(0, new Mock(whenFunctionName, whenExactMatchFunctionInput, true, thenAnswerOutput));
    }

    public void verifyPartial(String functionName, Map<String, Object> partialMatchFunctionInput) {
        verifyPartial(functionName, partialMatchFunctionInput, new UnlimitedNumberOfTimes());
    }

    public void verifyPartial(String functionName, Map<String, Object> partialMatchFunctionInput,
            VerificationTimes verificationTimes) {
        var matchesFound = 0;
        for (var invocation : invocations) {
            if (Objects.equals(invocation.functionName, functionName)) {
                if (InternalMockProcess.isSubMap(invocation.functionInput, partialMatchFunctionInput)) {
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
                        """.formatted(e.times, matchesFound, functionName, partialMatchFunctionInput));
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
                """.formatted(functionName, partialMatchFunctionInput));
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

    public void verifyExact(String functionName, Map<String, Object> exactMatchFunctionInput) {
        verifyExact(functionName, exactMatchFunctionInput, new UnlimitedNumberOfTimes());
    }

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

    public void clearInvocations() {
        this.invocations.clear();
    }
}
