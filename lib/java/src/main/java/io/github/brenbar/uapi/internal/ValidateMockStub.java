package io.github.brenbar.uapi.internal;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;

import io.github.brenbar.uapi.internal.types.UFn;
import io.github.brenbar.uapi.internal.types.UStruct;
import io.github.brenbar.uapi.internal.types.UType;
import io.github.brenbar.uapi.internal.types.UTypeDeclaration;
import io.github.brenbar.uapi.internal.types.UUnion;

import static io.github.brenbar.uapi.internal.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;
import static io.github.brenbar.uapi.internal.AsMap.asMap;
import static io.github.brenbar.uapi.internal.Prepend.prepend;

public class ValidateMockStub {
    public static List<ValidationFailure> validateMockStub(Object givenObj, Map<String, Object> select, String fn,
            List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics, Map<String, UType> types) {
        final var validationFailures = new ArrayList<ValidationFailure>();

        final Map<String, Object> givenMap;
        try {
            givenMap = asMap(givenObj);
        } catch (ClassCastException e) {
            return getTypeUnexpectedValidationFailure(List.of(), givenObj, "Object");
        }

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
        final Map<String, UStruct> functionDefCallCases = functionDefCall.cases;
        final var inputFailures = functionDefCallCases.get(functionDefName).validate(input, select, fn, List.of(),
                List.of());

        final var inputFailuresWithPath = new ArrayList<ValidationFailure>();
        for (final var f : inputFailures) {
            final List<Object> thisPath = prepend(functionName, f.path);

            inputFailuresWithPath.add(new ValidationFailure(thisPath, f.reason, f.data));
        }

        final var inputFailuresWithoutMissingRequired = inputFailuresWithPath.stream()
                .filter(f -> !Objects.equals(f.reason, "RequiredObjectKeyMissing")).toList();

        validationFailures.addAll(inputFailuresWithoutMissingRequired);

        final var resultDefKey = "->";

        if (!givenMap.containsKey(resultDefKey)) {
            validationFailures.add(new ValidationFailure(List.of(resultDefKey),
                    "RequiredObjectKeyMissing",
                    Map.of()));
        } else {
            final var output = givenMap.get(resultDefKey);
            final var outputFailures = functionDef.result.validate(output, select, fn, List.of(), List.of());

            final var outputFailuresWithPath = new ArrayList<ValidationFailure>();
            for (final var f : outputFailures) {
                final List<Object> thisPath = prepend(resultDefKey, f.path);

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
