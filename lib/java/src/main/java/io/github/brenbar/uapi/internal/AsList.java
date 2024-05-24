package io.github.brenbar.uapi.internal;

import java.util.List;

public class AsList {

    public static List<Object> asList(Object object) {
        if (object == null) {
            throw new ClassCastException();
        }

        return (List<Object>) object;
    }
}
