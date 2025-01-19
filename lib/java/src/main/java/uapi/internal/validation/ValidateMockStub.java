package uapi.internal.validation;

import static uapi.internal.validation.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;

import uapi.internal.types.UFn;
import uapi.internal.types.UStruct;
import uapi.internal.types.UType;
import uapi.internal.types.UTypeDeclaration;
import uapi.internal.types.UUnion;

public class ValidateMockStub {
    public static List<ValidationFailure> validateMockStub(Object givenObj,
            List<UTypeDeclaration> typeParameters, Map<String, UType> types, ValidateContext ctx) {
        final var validationFailures = new ArrayList<ValidationFailure>();

        if (!(givenObj instanceof Map)) {
            return getTypeUnexpectedValidationFailure(List.of(), givenObj, "Object");
        }
        final Map<String, Object> givenMap = (Map<String, Object>) givenObj;

        final var regexString = "^fn\\..*$";

        final var keys = givenMap.keySet().stream().sorted().toList();

        final var matches = keys.stream().filter(k -> k.matches(regexString)).toList();
        if (matches.size() != 1) {
            return List.of(
                    new ValidationFailure(List.of(),
                            "ObjectKeyRegexMatchCountUnexpected",
                            Map.of("regex", regexString, "actual",
                                    matches.size(), "expected", 1, "keys", keys)));

        }

        final var functionName = matches.get(0);
        final var functionDef = (UFn) types.get(functionName);
        final var input = givenMap.get(functionName);

        final UUnion functionDefCall = functionDef.call;
        final String functionDefName = functionDef.name;
        final Map<String, UStruct> functionDefCallTags = functionDefCall.tags;
        final var inputFailures = functionDefCallTags.get(functionDefName).validate(input, List.of(), ctx);

        final var inputFailuresWithPath = new ArrayList<ValidationFailure>();
        for (final var f : inputFailures) {
            final List<Object> thisPath = new ArrayList<>(f.path);
            thisPath.add(0, functionName);

            inputFailuresWithPath.add(new ValidationFailure(thisPath, f.reason, f.data));
        }

        final var inputFailuresWithoutMissingRequired = inputFailuresWithPath.stream()
                .filter(f -> !Objects.equals(f.reason, "RequiredObjectKeyMissing")).toList();

        validationFailures.addAll(inputFailuresWithoutMissingRequired);

        final var resultDefKey = "->";

        if (!givenMap.containsKey(resultDefKey)) {
            validationFailures.add(new ValidationFailure(List.of(),
                    "RequiredObjectKeyMissing",
                    Map.of("key", resultDefKey)));
        } else {
            final var output = givenMap.get(resultDefKey);
            final var outputFailures = functionDef.result.validate(output, List.of(), ctx);

            final var outputFailuresWithPath = new ArrayList<ValidationFailure>();
            for (final var f : outputFailures) {
                final List<Object> thisPath = new ArrayList<>(f.path);
                thisPath.add(0, resultDefKey);

                outputFailuresWithPath.add(new ValidationFailure(thisPath, f.reason, f.data));
            }

            final var failuresWithoutMissingRequired = outputFailuresWithPath
                    .stream()
                    .filter(f -> !Objects.equals(f.reason, "RequiredObjectKeyMissing"))
                    .toList();

            validationFailures.addAll(failuresWithoutMissingRequired);
        }

        final var disallowedFields = givenMap.keySet().stream()
                .filter(k -> !matches.contains(k) && !Objects.equals(k, resultDefKey)).toList();
        for (final var disallowedField : disallowedFields) {
            validationFailures
                    .add(new ValidationFailure(List.of(disallowedField), "ObjectKeyDisallowed", Map.of()));
        }

        return validationFailures;
    }
}
