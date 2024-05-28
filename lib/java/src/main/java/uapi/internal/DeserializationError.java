package uapi.internal;

public class DeserializationError extends RuntimeException {

    public DeserializationError(Throwable cause) {
        super(cause);
    }

    public DeserializationError(String message) {
        super(message);
    }

}
