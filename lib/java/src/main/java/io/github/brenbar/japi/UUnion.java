package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class UUnion implements UType {

    public final String name;
    public final Map<String, UStruct> cases;
    public final int typeParameterCount;

    public UUnion(String name, Map<String, UStruct> cases, int typeParameterCount) {
        this.name = name;
        this.cases = cases;
        this.typeParameterCount = typeParameterCount;
    }

    @Override
    public int getTypeParameterCount() {
        return this.typeParameterCount;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics) {
        if (value instanceof Map<?, ?> m) {
            return validateUnionCases(this.cases, m, typeParameters);
        } else {
            return _ValidateUtil.getTypeUnexpectedValidationFailure(List.of(), value,
                    this.getName(generics));
        }
    }

    private List<ValidationFailure> validateUnionCases(
            Map<String, UStruct> referenceCases,
            Map<?, ?> actual, List<UTypeDeclaration> typeParameters) {
        if (actual.size() != 1) {
            return Collections.singletonList(
                    new ValidationFailure(new ArrayList<Object>(),
                            "ZeroOrManyUnionFieldsDisallowed", Map.of()));
        }
        var entry = UUnion.entry((Map<String, Object>) actual);
        var unionTarget = (String) entry.getKey();
        var unionPayload = entry.getValue();

        var referenceStruct = referenceCases.get(unionTarget);
        if (referenceStruct == null) {
            return Collections
                    .singletonList(new ValidationFailure(List.of(unionTarget),
                            "UnionFieldUnknown", Map.of()));
        }

        if (unionPayload instanceof Map<?, ?> m2) {
            var nestedValidationFailures = validateUnionStruct(referenceStruct, unionTarget,
                    (Map<String, Object>) m2, typeParameters);
            var nestedValidationFailuresWithPath = nestedValidationFailures
                    .stream()
                    .map(f -> new ValidationFailure(_ValidateUtil.prepend(unionTarget, f.path), f.reason,
                            f.data))
                    .toList();
            return nestedValidationFailuresWithPath;
        } else {
            return _ValidateUtil.getTypeUnexpectedValidationFailure(List.of(unionTarget),
                    unionPayload, "Object");
        }
    }

    private static List<ValidationFailure> validateUnionStruct(
            UStruct unionStruct,
            String unionCase,
            Map<String, Object> actual, List<UTypeDeclaration> typeParameters) {
        var validationFailures = new ArrayList<ValidationFailure>();

        var nestedValidationFailures = UStruct.validateStructFields(unionStruct.fields,
                actual, typeParameters);
        validationFailures.addAll(nestedValidationFailures);

        return validationFailures;
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics,
            RandomGenerator random) {
        if (useStartingValue) {
            var startingUnionCase = (Map<String, Object>) startingValue;
            return constructRandomUnion(this.cases, startingUnionCase, includeRandomOptionalFields,
                    typeParameters, random);
        } else {
            return constructRandomUnion(this.cases, new HashMap<>(), includeRandomOptionalFields,
                    typeParameters, random);
        }
    }

    static Map<String, Object> constructRandomUnion(Map<String, UStruct> unionCasesReference,
            Map<String, Object> startingUnion,
            boolean includeRandomOptionalFields,
            List<UTypeDeclaration> typeParameters,
            RandomGenerator random) {
        if (!startingUnion.isEmpty()) {
            var unionEntry = UUnion.entry(startingUnion);
            var unionCase = unionEntry.getKey();
            var unionStructType = unionCasesReference.get(unionCase);
            var unionStartingStruct = (Map<String, Object>) startingUnion.get(unionCase);

            return Map.of(unionCase, UStruct.constructRandomStruct(unionStructType.fields, unionStartingStruct,
                    includeRandomOptionalFields, typeParameters, random));
        } else {
            var sortedUnionCasesReference = new ArrayList<>(unionCasesReference.entrySet());
            Collections.sort(sortedUnionCasesReference, (e1, e2) -> e1.getKey().compareTo(e2.getKey()));

            var randomIndex = random.nextInt(sortedUnionCasesReference.size());
            var unionEntry = sortedUnionCasesReference.get(randomIndex);

            var unionCase = unionEntry.getKey();
            var unionData = unionEntry.getValue();

            return Map.of(unionCase,
                    UStruct.constructRandomStruct(unionData.fields, new HashMap<>(), includeRandomOptionalFields,
                            typeParameters, random));
        }
    }

    static Map.Entry<String, Object> entry(Map<String, Object> union) {
        return union.entrySet().stream().findAny().orElse(null);
    }

    @Override
    public String getName(List<UTypeDeclaration> generics) {
        return "Object";
    }
}
