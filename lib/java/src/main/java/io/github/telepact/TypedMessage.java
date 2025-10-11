package io.github.telepact;

import java.util.Map;

public class TypedMessage<T> {

    public final Map<String, Object> headers;
    public final T body;

    public TypedMessage(Map<String, Object> headers, T body) {
        this.headers = headers;
        this.body = body;
    }
}
