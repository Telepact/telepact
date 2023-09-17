package io.github.brenbar.japi;

import java.util.Map;

public class MockVerification {
    final String functionName;
    final Map<String, Object> argument;
    boolean allowArgumentPartialMatch;
    VerificationTimes verificationTimes;

    public MockVerification(String functionName, Map<String, Object> argument) {
        this.functionName = functionName;
        this.argument = argument;
        this.allowArgumentPartialMatch = false;
        this.verificationTimes = new UnlimitedNumberOfTimes();
    }

    public MockVerification setAllowArgumentPartialMatch(boolean allowPartialArgumentMatch) {
        this.allowArgumentPartialMatch = allowPartialArgumentMatch;
        return this;
    }

    public MockVerification setVerificationTimes(VerificationTimes verificationTimes) {
        this.verificationTimes = verificationTimes;
        return this;
    }

    /**
     * Applies a criteria to the number of times a verification should be matched.
     */
    public sealed interface VerificationTimes
            permits UnlimitedNumberOfTimes, ExactNumberOfTimes, AtMostNumberOfTimes, AtLeastNumberOfTimes {

    }

    /**
     * Allows any number of matches for a verification query.
     */
    public final static class UnlimitedNumberOfTimes implements VerificationTimes {

    }

    /**
     * Allows only the given number of matches for a verification query.
     */
    public final static class ExactNumberOfTimes implements VerificationTimes {
        public final int times;

        public ExactNumberOfTimes(int times) {
            this.times = times;
        }
    }

    /**
     * Allows at most the given number of matches for a verification query.
     */
    public final static class AtMostNumberOfTimes implements VerificationTimes {
        public final int times;

        public AtMostNumberOfTimes(int times) {
            this.times = times;
        }
    }

    /**
     * Allows at least the given number of matches for a verification query.
     */
    public final static class AtLeastNumberOfTimes implements VerificationTimes {
        public final int times;

        public AtLeastNumberOfTimes(int times) {
            this.times = times;
        }
    }
}
