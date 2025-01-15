package uapi.internal.generation;

public class GenerateRandomNumber {
    public static Object generateRandomNumber(GenerateContext ctx) {
        if (ctx.useBlueprintValue) {
            return ctx.blueprintValue;
        } else {
            return ctx.randomGenerator.nextDouble();
        }
    }
}
