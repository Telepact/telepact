package io.github.telepact.internal.validation;

import java.util.Map;

public class ValidateContext {
    public final Map<String, Object> select;
    public final String fn;

    public ValidateContext(Map<String, Object> select, String fn) {
        this.select = select;
        this.fn = fn;
    }

}
