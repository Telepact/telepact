package io.github.brenbar.uapi.internal;

import java.util.Map;

public class _BinaryPackNode {
    public final Integer value;
    public final Map<Integer, _BinaryPackNode> nested;

    public _BinaryPackNode(Integer value, Map<Integer, _BinaryPackNode> nested) {
        this.value = value;
        this.nested = nested;
    }
}