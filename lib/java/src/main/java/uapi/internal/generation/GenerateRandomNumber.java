package uapi.internal.generation;

public class GenerateRandomNumber {
    public static Object generateRandomNumber(Object blueprintValue, boolean useBlueprintValue,
            GenerateContext ctx) {
        if (useBlueprintValue) {
            return blueprintValue;
        } else {
            return ctx.randomGenerator.nextDouble();
        }
    }
}
