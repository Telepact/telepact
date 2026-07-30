//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.validation;

import java.util.HashMap;
import java.util.Map;
import java.util.Stack;

public class ValidateContext {
    public final Stack<String> path;
    public final Map<String, Object> select;
    public final String fn;
    public final boolean coerceBase64;
    public final Map<String, Object> base64Coercions;
    public final Map<String, Object> bytesCoercions;


    public ValidateContext(Map<String, Object> select, String fn, boolean coerceBase64) {
        this.path = new Stack<>();
        this.select = select;
        this.fn = fn;
        this.coerceBase64 = coerceBase64;
        this.base64Coercions = new HashMap<>();
        this.bytesCoercions = new HashMap<>();

    }

}
