package io.github.brenbar.uapi.internal;

public class AsString {
    public static String asString(Object object) {
        if (object == null) {
            throw new ClassCastException();
        }

        return (String) object;
    }
}
