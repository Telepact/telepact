package io.github.brenbar.uapi;

import java.util.Map;

class _MockStub {
    final String whenFunction;
    final Map<String, Object> whenArgument;
    final Map<String, Object> thenResult;
    final boolean allowArgumentPartialMatch;

    public _MockStub(String whenFunction, Map<String, Object> whenArgument,
            Map<String, Object> thenResult, boolean allowArgumentPartialMatch) {
        this.whenFunction = whenFunction;
        this.whenArgument = whenArgument;
        this.thenResult = thenResult;
        this.allowArgumentPartialMatch = allowArgumentPartialMatch;
    }
}
