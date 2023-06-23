package io.github.brenbar.japi;

import java.util.HashMap;
import java.util.Map;

public class Context {
    public final String functionName;
    public final Map<String, Object> properties = new HashMap<String, Object>();

    public Context(String functionName) {
        this.functionName = functionName;
    }
}