package io.github.telepact;

import java.util.Map;

public class Response {
    public final byte[] bytes;
    public final Map<String, Object> headers;

    public Response(byte[] bytes, Map<String, Object> headers) {
        this.bytes = bytes;
        this.headers = headers;
    }
    
}
