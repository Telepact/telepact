package io.github.brenbar.uapi.internal.validation;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;

import io.github.brenbar.uapi.internal.types.UStruct;
import io.github.brenbar.uapi.internal.types.UTypeDeclaration;

import static io.github.brenbar.uapi.internal.UnionEntry.unionEntry;
import static io.github.brenbar.uapi.internal.validation.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;
import static io.github.brenbar.uapi.internal.validation.ValidateUnionStruct.validateUnionStruct;

public class ValidateUnionCases {
    static List<ValidationFailure> validateUnionCases(
            Map<String, UStruct> referenceCases, Map<String, Object> selectedCases,
            Map<?, ?> actual, Map<String, Object> select, String fn, List<UTypeDeclaration> typeParameters) {
        if (actual.size() != 1) {
            return List.of(
                    new ValidationFailure(new ArrayList<Object>(),
                            "ObjectSizeUnexpected", Map.of("actual", actual.size(), "expected", 1)));
        }

        final var entry = unionEntry((Map<String, Object>) actual);
        final var unionTarget = (String) entry.getKey();
        final var unionPayload = entry.getValue();

        final var referenceStruct = referenceCases.get(unionTarget);
        if (referenceStruct == null) {
            return Collections
                    .singletonList(new ValidationFailure(List.of(unionTarget),
                            "ObjectKeyDisallowed", Map.of()));
        }

        if (unionPayload instanceof Map<?, ?> m2) {
            final var nestedValidationFailures = validateUnionStruct(referenceStruct, unionTarget,
                    (Map<String, Object>) m2, selectedCases, select, fn, typeParameters);

            final var nestedValidationFailuresWithPath = new ArrayList<ValidationFailure>();
            for (final var f : nestedValidationFailures) {
                final List<Object> thisPath = new ArrayList<>(f.path);
                thisPath.add(0, unionTarget);

                nestedValidationFailuresWithPath.add(new ValidationFailure(thisPath, f.reason, f.data));
            }

            return nestedValidationFailuresWithPath;
        } else {
            return getTypeUnexpectedValidationFailure(List.of(unionTarget),
                    unionPayload, "Object");
        }
    }
}
