package io.github.brenbar.japi;

import java.util.Map;

public class MockStub {
    final String whenFunction;
    final Map<String, Object> whenArgument;
    final Map<String, Object> thenResult;
    boolean allowArgumentPartialMatch;
    boolean generateMissingResultFields;

    public MockStub(String whenFunction, Map<String, Object> whenArgument,
            Map<String, Object> thenResult) {
        this.whenFunction = whenFunction;
        this.whenArgument = whenArgument;
        this.thenResult = thenResult;
        this.allowArgumentPartialMatch = false;
        this.generateMissingResultFields = false;
    }

    public MockStub setAllowArgumentPartialMatch(boolean allowPartialArgumentMatch) {
        this.allowArgumentPartialMatch = allowPartialArgumentMatch;
        return this;
    }

    public MockStub setGenerateMissingResultFields(boolean generateMissingResultFields) {
        this.generateMissingResultFields = generateMissingResultFields;
        return this;
    }
}
