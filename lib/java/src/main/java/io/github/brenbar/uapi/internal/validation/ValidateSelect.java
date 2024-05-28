package io.github.brenbar.uapi.internal.validation;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import io.github.brenbar.uapi.internal.types.UFn;
import io.github.brenbar.uapi.internal.types.UStruct;
import io.github.brenbar.uapi.internal.types.UType;
import io.github.brenbar.uapi.internal.types.UTypeDeclaration;
import io.github.brenbar.uapi.internal.types.UUnion;

import static io.github.brenbar.uapi.internal.validation.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;
import static io.github.brenbar.uapi.internal.validation.ValidateSelectStruct.validateSelectStruct;

public class ValidateSelect {
    public static List<ValidationFailure> validateSelect(Object givenObj, Map<String, Object> select, String fn,
            List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics, Map<String, UType> types) {

        if (!(givenObj instanceof Map)) {
            return getTypeUnexpectedValidationFailure(List.of(), givenObj, "Object");
        }
        final Map<String, Object> selectStructFieldsHeader = (Map<String, Object>) givenObj;

        final var validationFailures = new ArrayList<ValidationFailure>();
        final var functionType = (UFn) types.get(fn);

        for (final var entry : selectStructFieldsHeader.entrySet()) {
            final var typeName = entry.getKey();
            final var selectValue = entry.getValue();

            final UType typeReference;
            if (typeName.equals("->")) {
                typeReference = functionType.result;
            } else {
                typeReference = types.get(typeName);
            }

            if (typeReference == null) {
                validationFailures.add(new ValidationFailure(List.of(typeName),
                        "ObjectKeyDisallowed", Map.of()));
                continue;
            }

            if (typeReference instanceof final UUnion u) {
                if (!(selectValue instanceof Map)) {
                    validationFailures.addAll(
                            getTypeUnexpectedValidationFailure(List.of(typeName), selectValue, "Object"));
                    continue;
                }
                final Map<String, Object> unionCases = (Map<String, Object>) selectValue;

                for (final var unionCaseEntry : unionCases.entrySet()) {
                    final var unionCase = unionCaseEntry.getKey();
                    final var selectedCaseStructFields = unionCaseEntry.getValue();
                    final var structRef = u.cases.get(unionCase);

                    final List<Object> loopPath = List.of(typeName, unionCase);

                    if (structRef == null) {
                        validationFailures.add(new ValidationFailure(
                                loopPath,
                                "ObjectKeyDisallowed", Map.of()));
                        continue;
                    }

                    final var nestedValidationFailures = validateSelectStruct(structRef, loopPath,
                            selectedCaseStructFields);

                    validationFailures.addAll(nestedValidationFailures);
                }
            } else if (typeReference instanceof final UFn f) {
                final UUnion fnCall = f.call;
                final Map<String, UStruct> fnCallCases = fnCall.cases;
                final String fnName = f.name;
                final var argStruct = fnCallCases.get(fnName);
                final var nestedValidationFailures = validateSelectStruct(argStruct, List.of(typeName),
                        selectValue);

                validationFailures.addAll(nestedValidationFailures);
            } else {
                final var structRef = (UStruct) typeReference;
                final var nestedValidationFailures = validateSelectStruct(structRef, List.of(typeName),
                        selectValue);

                validationFailures.addAll(nestedValidationFailures);
            }
        }

        return validationFailures;
    }
}
