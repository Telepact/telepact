package io.github.brenbar.japi;

import java.util.List;
import java.util.Map;

public class Error extends RuntimeException {
    public Error(String message) {
        super(message);
    }

    public Error(Throwable cause) {
        super(cause);
    }

    public Error() {
        super();
    }

    public static class ApplicationFailure extends RuntimeException {
        public final String messageType;
        public final Map<String, Object> body;

        public ApplicationFailure(String messageType, Map<String, Object> body) {
            this.messageType = messageType;
            this.body = body;
        }
    }

    static class JapiMessageArrayTooFewElements extends Error {
    }

    static class JapiMessageNotArray extends Error {
    }

    static class JapiMessageTypeNotString extends Error {
    }

    static class JapiMessageTypeNotFunction extends Error {
    }

    static class JapiMessageHeaderNotObject extends Error {
    }

    static class InvalidBinaryEncoding extends Error {
    }

    static class InvalidSelectFieldsHeader extends Error {
    }

    static class BinaryDecodeFailure extends Error {
        public BinaryDecodeFailure(Throwable cause) {
            super(cause);
        }
    }

    static class JapiMessageBodyNotObject extends Error {
    }

    static class FunctionNotFound extends Error {
        public final String functionName;

        public FunctionNotFound(String functionName) {
            super("Function not found: %s".formatted(functionName));
            this.functionName = functionName;
        }
    }

    static class InvalidInput extends Error {
        public InvalidInput() {
            super();
        }

        public InvalidInput(Throwable cause) {
            super(cause);
        }

    }

    static class InvalidOutput extends Error {
        public InvalidOutput(Throwable cause) {
            super(cause);
        }
    }

    static class InvalidApplicationFailure extends Error {
        public InvalidApplicationFailure(Throwable cause) {
            super(cause);
        }
    }

    static class DisallowedError extends Error {
        public DisallowedError(Throwable cause) {
            super(cause);
        }
    }

    static class FieldError extends InvalidInput {
        public FieldError() {
            super();
        }

        public FieldError(Throwable cause) {
            super(cause);
        }
    }

    static class StructMissingFields extends FieldError {
        public final String namespace;
        public final List<String> missingFields;

        public StructMissingFields(String namespace, List<String> missingFields) {
            super();
            this.namespace = namespace;
            this.missingFields = missingFields;
        }
    }

    static class StructHasExtraFields extends FieldError {
        public final String namespace;
        public final List<String> extraFields;

        public StructHasExtraFields(String namespace, List<String> extraFields) {
            super();
            this.namespace = namespace;
            this.extraFields = extraFields;
        }
    }

    static class EnumDoesNotHaveOnlyOneField extends FieldError {
        public final String namespace;

        public EnumDoesNotHaveOnlyOneField(String namespace) {
            super();
            this.namespace = namespace;
        }
    }

    static class UnknownEnumField extends FieldError {
        public final String namespace;
        public final String field;

        public UnknownEnumField(String namespace, String field) {
            super();
            this.namespace = namespace;
            this.field = field;
        }
    }

    static class InvalidFieldType extends FieldError {
        public final String fieldName;
        public final InvalidFieldTypeError error;

        public InvalidFieldType(String fieldName, InvalidFieldTypeError error) {
            this.fieldName = fieldName;
            this.error = error;
        }

        public InvalidFieldType(String fieldName, InvalidFieldTypeError error, Throwable cause) {
            super(cause);
            this.fieldName = fieldName;
            this.error = error;
        }
    }
}
