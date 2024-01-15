package io.github.brenbar.uapi;

import java.util.List;
import java.util.Map;

class _CastUtil {

    public static Integer asInt(Object object) {
        if (object == null) {
            throw new ClassCastException();
        }
        return (Integer) object;
    }

    public static Long asLong(Object object) {
        if (object == null) {
            throw new ClassCastException();
        }
        return (Long) object;
    }

    public static String asString(Object object) {
        if (object == null) {
            throw new ClassCastException();
        }
        return (String) object;
    }

    public static List<Object> asList(Object object) {
        if (object == null) {
            throw new ClassCastException();
        }
        return (List<Object>) object;
    }

    public static Map<String, Object> asMap(Object object) {
        if (object == null) {
            throw new ClassCastException();
        }
        return (Map<String, Object>) object;
    }

}
