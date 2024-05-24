package io.github.brenbar.uapi.internal.types;

import java.util.Map;

public class UHeaders {
    public final String name;
    public final Map<String, UFieldDeclaration> requestHeaders;
    public final Map<String, UFieldDeclaration> responseHeaders;

    public UHeaders(
            final String name,
            final Map<String, UFieldDeclaration> requestHeaders,
            final Map<String, UFieldDeclaration> responseHeaders) {
        this.name = name;
        this.requestHeaders = requestHeaders;
        this.responseHeaders = responseHeaders;
    }
}
