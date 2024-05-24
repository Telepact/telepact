package io.github.brenbar.uapi.internal;

import java.util.Map;

public class _UHeaders {
    public final String name;
    public final Map<String, _UFieldDeclaration> requestHeaders;
    public final Map<String, _UFieldDeclaration> responseHeaders;

    public _UHeaders(
            final String name,
            final Map<String, _UFieldDeclaration> requestHeaders,
            final Map<String, _UFieldDeclaration> responseHeaders) {
        this.name = name;
        this.requestHeaders = requestHeaders;
        this.responseHeaders = responseHeaders;
    }
}
