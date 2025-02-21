package uapitest;

import java.util.function.Consumer;

public class Optional_<T> {

    private final T value;
    private final boolean isPresent;

    public Optional_() {
        this.value = null;
        this.isPresent = false;
    }

    public Optional_(T value) {
        this.value = value;
        this.isPresent = true;
    }

    public boolean ifPresent(Consumer<T> consumer) {
        if (this.isPresent) {
            consumer.accept(this.value);
            return true;
        } else {
            return false;
        }
    }

    public boolean ifPresentOrElse(Consumer<T> consumer, Runnable emptyAction) {
        if (this.isPresent) {
            consumer.accept(this.value);
            return true;
        } else {
            emptyAction.run();
            return false;
        }
    }
}