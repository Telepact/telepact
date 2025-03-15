package io.github.msgpact.internal.types;

import java.util.Map;

public class VHeaders {
    public final String name;
    public final Map<String, VFieldDeclaration> requestHeaders;
    public final Map<String, VFieldDeclaration> responseHeaders;

    public VHeaders(
            final String name,
            final Map<String, VFieldDeclaration> requestHeaders,
            final Map<String, VFieldDeclaration> responseHeaders) {
        this.name = name;
        this.requestHeaders = requestHeaders;
        this.responseHeaders = responseHeaders;
    }
}
