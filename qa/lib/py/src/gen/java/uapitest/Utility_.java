package uapitest;

import java.util.function.Function;

public class Utility_ {

    public static <T, U> U let(T value, Function<T, U> f) {
        return f.apply(value);
    }

}