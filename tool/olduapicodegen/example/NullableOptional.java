package example;

public class NullableOptional<T> {
    private final T value;
    private final boolean present;

    private NullableOptional(T value, boolean present) {
        this.value = value;
        this.present = present;
    }

    public static <T> NullableOptional<T> of(T value) {
        return new NullableOptional<>(value, true);
    }

    public static <T> NullableOptional<T> empty() {
        return new NullableOptional<>(null, false);
    }

    public boolean isPresent() {
        return present;
    }

    public T get() {
        return value;
    }
}
