package io.github.brenbar.uapi.internal;

import java.util.Map;

public class BinaryPackNode {
    public final Integer value;
    public final Map<Integer, BinaryPackNode> nested;

    public BinaryPackNode(Integer value, Map<Integer, BinaryPackNode> nested) {
        this.value = value;
        this.nested = nested;
    }
}