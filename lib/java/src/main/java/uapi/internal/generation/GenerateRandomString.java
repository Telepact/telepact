package uapi.internal.generation;

public class GenerateRandomString {
    public static Object generateRandomString(GenerateContext ctx) {
        if (ctx.useBlueprintValue) {
            return ctx.blueprintValue;
        } else {
            return ctx.randomGenerator.nextString();
        }
    }
}
