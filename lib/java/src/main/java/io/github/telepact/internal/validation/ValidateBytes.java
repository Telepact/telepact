package io.github.telepact.internal.validation;

import static io.github.telepact.internal.types.TBytes._BYTES_NAME;

import java.util.Base64;
import java.util.List;
import java.util.Map;

public class ValidateBytes {

    public static List<ValidationFailure> validateBytes(Object value, ValidateContext ctx) {
        System.out.println("Validating value: " + value + " with context: " + ctx);

        if (value instanceof byte[]) {
            System.out.println("Value is a byte array.");
            if (ctx.coerceBase64) {
                System.out.println("Coercing Base64 for byte array.");
                setCoercedPath(ctx.path, ctx.base64Coercions);
            }
            return List.of();
        } else if (value instanceof String) {
            System.out.println("Value is a String.");
            try {
                Base64.getDecoder().decode((String) value);
                System.out.println("String is valid Base64.");
                if (!ctx.coerceBase64) {
                    System.out.println("Coercing bytes for Base64 string.");
                    setCoercedPath(ctx.path, ctx.bytesCoercions);
                }
                return List.of();
            } catch (IllegalArgumentException e) {
                System.out.println("String is not valid Base64: " + e.getMessage());
                return GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure(
                    List.of(), value, "Base64String"
                );
            }
        } else {
            System.out.println("Value is of unexpected type: " + value.getClass().getName());
            return GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure(
                List.of(), value, _BYTES_NAME
            );
        }
    }

    private static void setCoercedPath(List<String> path, Map<String, Object> coercedPath) {
        System.out.println("Setting coerced path: " + path + " into: " + coercedPath);
        String part = path.get(0);
        System.out.println("Processing path part: " + part);

        if (path.size() > 1) {
            System.out.println("Path has more parts, recursing...");
            coercedPath.putIfAbsent(part, new java.util.HashMap<String, Object>());
            setCoercedPath(path.subList(1, path.size()), (Map<String, Object>) coercedPath.get(part));
        } else {
            System.out.println("Final path part reached, setting value to true.");
            coercedPath.put(part, true);
        }
    }
}