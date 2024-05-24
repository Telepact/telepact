package io.github.brenbar.uapi.internal;

public class AsInt {
    public static Integer asInt(Object object) {
        if (object == null) {
            throw new ClassCastException();
        }

        return (Integer) object;
    }
}
