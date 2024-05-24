package io.github.brenbar.uapi.internal;

import java.util.ArrayList;
import java.util.List;

public class Prepend {

    public static List<Object> prepend(Object value, List<Object> original) {
        final var newList = new ArrayList<>(original);

        newList.add(0, value);
        return newList;
    }
}
