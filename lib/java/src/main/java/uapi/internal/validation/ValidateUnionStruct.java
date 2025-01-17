package uapi.internal.validation;

import static uapi.internal.validation.ValidateStructFields.validateStructFields;

import java.util.List;
import java.util.Map;

import uapi.internal.types.UStruct;

public class ValidateUnionStruct {
    static List<ValidationFailure> validateUnionStruct(
            UStruct unionStruct,
            String unionCase,
            Map<String, Object> actual, Map<String, Object> selectedCases, ValidateContext ctx) {
        final var selectedFields = selectedCases == null ? null : (List<String>) selectedCases.get(unionCase);
        return validateStructFields(unionStruct.fields, selectedFields, actual, ctx);
    }
}
