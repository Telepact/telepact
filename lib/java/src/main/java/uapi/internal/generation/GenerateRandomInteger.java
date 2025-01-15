package uapi.internal.generation;

public class GenerateRandomInteger {
    public static Object generateRandomInteger(GenerateContext ctx) {
        if (ctx.useBlueprintValue) {
            return ctx.blueprintValue;
        } else {
            return ctx.randomGenerator.nextInt();
        }
    }
}
