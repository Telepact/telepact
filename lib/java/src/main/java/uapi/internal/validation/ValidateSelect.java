package uapi.internal.validation;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class ValidateSelect {

    public static List<ValidationFailure> validateSelect(Object givenObj,
            Map<String, Object> possibleFnSelects, ValidateContext ctx) {
        if (!(givenObj instanceof Map) || givenObj == null) {
            return GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure(new ArrayList<>(), givenObj,
                    "Object");
        }

        Map<String, Object> possibleSelect = (Map<String, Object>) possibleFnSelects.get(ctx.fn);

        return isSubSelect(new ArrayList<>(), givenObj, possibleSelect);
    }

    private static List<ValidationFailure> isSubSelect(List<Object> path, Object givenObj,
            Object possibleSelectSection) {

        if (possibleSelectSection instanceof List) {
            if (!(givenObj instanceof List)) {
                return GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure(path, givenObj, "Array");
            }

            List<ValidationFailure> validationFailures = new ArrayList<>();

            List<?> givenObjList = (List<?>) givenObj;
            List<?> possibleSelectList = (List<?>) possibleSelectSection;

            for (int index = 0; index < givenObjList.size(); index++) {
                Object element = givenObjList.get(index);
                if (!possibleSelectList.contains(element)) {
                    var loopPath = new ArrayList<>(path);
                    loopPath.add(index);
                    validationFailures.add(new ValidationFailure(loopPath, "ArrayElementDisallowed", Map.of()));
                }
            }

            return validationFailures;
        } else if (possibleSelectSection instanceof Map) {
            if (!(givenObj instanceof Map) || givenObj == null) {
                return GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure(path, givenObj, "Object");
            }

            List<ValidationFailure> validationFailures = new ArrayList<>();

            Map<String, Object> givenObjMap = (Map<String, Object>) givenObj;
            Map<String, Object> possibleSelectMap = (Map<String, Object>) possibleSelectSection;

            for (Map.Entry<String, Object> entry : givenObjMap.entrySet()) {
                String key = entry.getKey();
                Object value = entry.getValue();
                if (possibleSelectMap.containsKey(key)) {
                    var loopPath = new ArrayList<>(path);
                    loopPath.add(key);
                    List<ValidationFailure> innerFailures = isSubSelect(loopPath, value, possibleSelectMap.get(key));
                    validationFailures.addAll(innerFailures);
                } else {
                    validationFailures.add(new ValidationFailure(new ArrayList<>(path) {
                        {
                            add(key);
                        }
                    }, "ObjectKeyDisallowed", Map.of()));
                }
            }

            return validationFailures;
        }

        return new ArrayList<>();
    }
}
