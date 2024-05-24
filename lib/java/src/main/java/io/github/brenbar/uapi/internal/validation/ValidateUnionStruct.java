package io.github.brenbar.uapi.internal.validation;

import static io.github.brenbar.uapi.internal.validation.ValidateStructFields.validateStructFields;

import java.util.List;
import java.util.Map;

import io.github.brenbar.uapi.internal.types.UStruct;
import io.github.brenbar.uapi.internal.types.UTypeDeclaration;

public class ValidateUnionStruct {
    static List<ValidationFailure> validateUnionStruct(
            UStruct unionStruct,
            String unionCase,
            Map<String, Object> actual, Map<String, Object> selectedCases, Map<String, Object> select, String fn,
            List<UTypeDeclaration> typeParameters) {
        final var selectedFields = selectedCases == null ? null : (List<String>) selectedCases.get(unionCase);
        return validateStructFields(unionStruct.fields, selectedFields, actual, select, fn, typeParameters);
    }
}
