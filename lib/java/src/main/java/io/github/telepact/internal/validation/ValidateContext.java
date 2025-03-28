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

package io.github.telepact.internal.validation;

import java.util.HashMap;
import java.util.Map;
import java.util.Stack;

public class ValidateContext {
    public final Stack<String> path;
    public final Map<String, Object> select;
    public final String fn;
    public final boolean expectBytes;
    public final boolean useBytes;
    public Object newValue;
    public final Map<String, Object> coercions;

    public ValidateContext(Map<String, Object> select, String fn, boolean expectBytes, boolean useBytes) {
        this.path = new Stack<>();
        this.select = select;
        this.fn = fn;
        this.expectBytes = expectBytes;
        this.useBytes = useBytes;
        this.newValue = null;
        this.coercions = new HashMap<>();
    }

}
