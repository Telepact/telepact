package uapi.internal.generation;

public class GenerateRandomBoolean {
    public static Object generateRandomBoolean(GenerateContext ctx) {
        if (ctx.useBlueprintValue) {
            return ctx.blueprintValue;
        } else {
            return ctx.randomGenerator.nextBoolean();
        }
    }
}
