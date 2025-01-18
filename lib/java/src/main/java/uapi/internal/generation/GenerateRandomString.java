package uapi.internal.generation;

public class GenerateRandomString {
    public static Object generateRandomString(Object blueprintValue, boolean useBlueprintValue,
            GenerateContext ctx) {
        if (useBlueprintValue) {
            return blueprintValue;
        } else {
            return ctx.randomGenerator.nextString();
        }
    }
}
