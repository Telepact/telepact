//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.types;

import java.util.Map;

public class THeaders {
    public final String name;
    public final Map<String, TFieldDeclaration> requestHeaders;
    public final Map<String, TFieldDeclaration> responseHeaders;

    public THeaders(
            final String name,
            final Map<String, TFieldDeclaration> requestHeaders,
            final Map<String, TFieldDeclaration> responseHeaders) {
        this.name = name;
        this.requestHeaders = requestHeaders;
        this.responseHeaders = responseHeaders;
    }
}
