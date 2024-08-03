package src.uapicodegen.templates;

public class Optional_<T> {

    public final T value;
    public final boolean isPresent;

    public Optional_() {
        this.value = null;
        this.isPresent = false;
    }

    public Optional_(T value) {
        this.value = value;
        this.isPresent = true;
    }
}
