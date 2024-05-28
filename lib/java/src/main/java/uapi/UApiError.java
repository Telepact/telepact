package uapi;

/**
 * Indicates critical failure in uAPI processing logic.
 */
public class UApiError extends RuntimeException {

    public UApiError(String message) {
        super(message);
    }

    public UApiError(Throwable cause) {
        super(cause);
    }
}
