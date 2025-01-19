package uapi.internal.validation;

import static uapi.internal.validation.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import uapi.internal.types.UFn;
import uapi.internal.types.UStruct;
import uapi.internal.types.UType;
import uapi.internal.types.UTypeDeclaration;
import uapi.internal.types.UUnion;

public class ValidateMockCall {
    public static List<ValidationFailure> validateMockCall(Object givenObj,
            List<UTypeDeclaration> typeParameters, Map<String, UType> types, ValidateContext ctx) {
        if (!(givenObj instanceof Map)) {
            return getTypeUnexpectedValidationFailure(new ArrayList<Object>(), givenObj, "Object");
        }
        final Map<String, Object> givenMap = (Map<String, Object>) givenObj;

        final var regexString = "^fn\\..*$";

        final var keys = givenMap.keySet().stream().sorted().toList();

        final var matches = keys.stream().filter(k -> k.matches(regexString)).toList();
        if (matches.size() != 1) {
            return List.of(new ValidationFailure(new ArrayList<Object>(), "ObjectKeyRegexMatchCountUnexpected",
                    Map.of("regex", regexString, "actual", matches.size(), "expected", 1, "keys", keys)));
        }

        final var functionName = matches.get(0);
        final var functionDef = (UFn) types.get(functionName);
        final var input = givenMap.get(functionName);

        final UUnion functionDefCall = functionDef.call;
        final String functionDefName = functionDef.name;
        final Map<String, UStruct> functionDefCallTags = functionDefCall.tags;

        final var inputFailures = functionDefCallTags.get(functionDefName).validate(input, List.of(), ctx);

        final var inputFailuresWithPath = new ArrayList<ValidationFailure>();
        for (var f : inputFailures) {
            List<Object> newPath = new ArrayList<>(f.path);
            newPath.add(0, functionName);

            inputFailuresWithPath.add(new ValidationFailure(newPath, f.reason, f.data));
        }

        return inputFailuresWithPath.stream()
                .filter(f -> !f.reason.equals("RequiredObjectKeyMissing")).toList();
    }
}
