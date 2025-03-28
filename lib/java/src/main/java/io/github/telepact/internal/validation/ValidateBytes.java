package io.github.telepact.internal.validation;

import static io.github.telepact.internal.validation.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;
import static io.github.telepact.internal.types.TBytes.getBytesName;

import java.util.Base64;
import java.util.List;
import java.util.Map;

public class ValidateBytes {

    public static List<ValidationFailure> validateBytes(Object value, ValidateContext ctx) {
        String expectedType = getBytesName(ctx);

        System.out.println("validating bytes: " + value);
        System.out.println("type: " + value.getClass());
        System.out.println("Is " + value.getClass() + " == bytes? " + (value instanceof byte[]));

        if (ctx.useBytes) {
            if (value instanceof byte[]) {
                return List.of();
            } else if (value instanceof String) {
                try {
                    byte[] newBytesValue = Base64.getDecoder().decode((String) value);
                    ctx.newValue = newBytesValue;
                    return List.of();
                } catch (Exception e) {
                    return getTypeUnexpectedValidationFailure(List.of(), value, expectedType);
                }
            } else {
                return getTypeUnexpectedValidationFailure(List.of(), value, expectedType);
            }
        } else {
            if (value instanceof String) {
                try {
                    Base64.getDecoder().decode((String) value);
                    return List.of();
                } catch (Exception e) {
                    return getTypeUnexpectedValidationFailure(List.of(), value, expectedType);
                }
            } else if (value instanceof byte[]) {
                String newB64Value = Base64.getEncoder().encodeToString((byte[]) value);
                ctx.newValue = newB64Value;

                setCoercedPath(ctx.path, ctx.coercions);

                return List.of();
            } else {
                return getTypeUnexpectedValidationFailure(List.of(), value, expectedType);
            }
        }
    }

    private static void setCoercedPath(List<String> path, Map<String, Object> coercedPath) {
        String part = path.get(0);

        if (path.size() > 1) {
            coercedPath.putIfAbsent(part, new java.util.HashMap<String, Object>());
            setCoercedPath(path.subList(1, path.size()), (Map<String, Object>) coercedPath.get(part));
        } else {
            coercedPath.put(part, true);
        }
    }
}