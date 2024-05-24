package io.github.brenbar.uapi.internal;

import java.util.Map;

public class _MockInvocation {
    public final String functionName;
    public final Map<String, Object> functionArgument;
    public boolean verified = false;

    public _MockInvocation(String functionName, Map<String, Object> functionArgument) {
        this.functionName = functionName;
        this.functionArgument = functionArgument;
    }
}
