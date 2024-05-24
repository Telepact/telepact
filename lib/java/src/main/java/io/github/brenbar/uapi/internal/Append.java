package io.github.brenbar.uapi.internal;

import java.util.ArrayList;
import java.util.List;

public class Append {
    public static List<Object> append(List<Object> original, Object value) {
        final var newList = new ArrayList<>(original);

        newList.add(value);
        return newList;
    }
}
