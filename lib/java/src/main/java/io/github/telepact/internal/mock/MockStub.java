package io.github.telepact.internal.mock;

import java.util.Map;

public class MockStub {
    final String whenFunction;
    final Map<String, Object> whenArgument;
    final Map<String, Object> thenResult;
    final boolean allowArgumentPartialMatch;
    int count;

    public MockStub(String whenFunction, Map<String, Object> whenArgument,
            Map<String, Object> thenResult, boolean allowArgumentPartialMatch, int count) {
        this.whenFunction = whenFunction;
        this.whenArgument = whenArgument;
        this.thenResult = thenResult;
        this.allowArgumentPartialMatch = allowArgumentPartialMatch;
        this.count = count;
    }
}
