//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

package io.github.telepact.internal.types;

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
