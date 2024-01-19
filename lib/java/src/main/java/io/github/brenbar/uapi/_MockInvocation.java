package io.github.brenbar.uapi;

import java.util.Map;

class _MockInvocation {
    public final String functionName;
    public final Map<String, Object> functionArgument;
    public boolean verified = false;

    public _MockInvocation(String functionName, Map<String, Object> functionArgument) {
        this.functionName = functionName;
        this.functionArgument = functionArgument;
    }
}
