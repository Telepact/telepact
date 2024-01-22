package io.github.brenbar.uapi;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

class _UUnion implements _UType {

    public final String name;
    public final Map<String, _UStruct> cases;
    public final int typeParameterCount;

    public _UUnion(String name, Map<String, _UStruct> cases, int typeParameterCount) {
        this.name = name;
        this.cases = cases;
        this.typeParameterCount = typeParameterCount;
    }

    @Override
    public int getTypeParameterCount() {
        return this.typeParameterCount;
    }

    @Override
    public List<_ValidationFailure> validate(Object value, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        if (value instanceof Map<?, ?> m) {
            return validateUnionCases(this.cases, m, typeParameters);
        } else {
            return _ValidateUtil.getTypeUnexpectedValidationFailure(List.of(), value,
                    this.getName(generics));
        }
    }

    private List<_ValidationFailure> validateUnionCases(
            Map<String, _UStruct> referenceCases,
            Map<?, ?> actual, List<_UTypeDeclaration> typeParameters) {
        if (actual.size() != 1) {
            return List.of(
                    new _ValidationFailure(new ArrayList<Object>(),
                            "ZeroOrManyUnionFieldsDisallowed", Map.of()));
        }
        final var entry = _UUnion.entry((Map<String, Object>) actual);
        final var unionTarget = (String) entry.getKey();
        final var unionPayload = entry.getValue();

        final var referenceStruct = referenceCases.get(unionTarget);
        if (referenceStruct == null) {
            return Collections
                    .singletonList(new _ValidationFailure(List.of(unionTarget),
                            "UnionFieldUnknown", Map.of()));
        }

        if (unionPayload instanceof Map<?, ?> m2) {
            final var nestedValidationFailures = validateUnionStruct(referenceStruct, unionTarget,
                    (Map<String, Object>) m2, typeParameters);

            final var nestedValidationFailuresWithPath = new ArrayList<_ValidationFailure>();
            for (final var f : nestedValidationFailures) {
                final List<Object> thisPath = _ValidateUtil.prepend(unionTarget, f.path);

                nestedValidationFailuresWithPath.add(new _ValidationFailure(thisPath, f.reason, f.data));
            }

            return nestedValidationFailuresWithPath;
        } else {
            return _ValidateUtil.getTypeUnexpectedValidationFailure(List.of(unionTarget),
                    unionPayload, "Object");
        }
    }

    private static List<_ValidationFailure> validateUnionStruct(
            _UStruct unionStruct,
            String unionCase,
            Map<String, Object> actual, List<_UTypeDeclaration> typeParameters) {
        return _UStruct.validateStructFields(unionStruct.fields, actual, typeParameters);
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator random) {
        if (useStartingValue) {
            final var startingUnionCase = (Map<String, Object>) startingValue;
            return constructRandomUnion(this.cases, startingUnionCase, includeRandomOptionalFields,
                    typeParameters, random);
        } else {
            return constructRandomUnion(this.cases, new HashMap<>(), includeRandomOptionalFields,
                    typeParameters, random);
        }
    }

    static Map<String, Object> constructRandomUnion(Map<String, _UStruct> unionCasesReference,
            Map<String, Object> startingUnion,
            boolean includeRandomOptionalFields,
            List<_UTypeDeclaration> typeParameters,
            _RandomGenerator randomGenerator) {
        if (!startingUnion.isEmpty()) {
            final var unionEntry = _UUnion.entry(startingUnion);
            final var unionCase = unionEntry.getKey();
            final var unionStructType = unionCasesReference.get(unionCase);
            final var unionStartingStruct = (Map<String, Object>) startingUnion.get(unionCase);

            return Map.of(unionCase, _UStruct.constructRandomStruct(unionStructType.fields, unionStartingStruct,
                    includeRandomOptionalFields, typeParameters, randomGenerator));
        } else {
            final var sortedUnionCasesReference = new ArrayList<>(unionCasesReference.entrySet());

            Collections.sort(sortedUnionCasesReference, (e1, e2) -> e1.getKey().compareTo(e2.getKey()));

            final var randomIndex = randomGenerator.nextInt(sortedUnionCasesReference.size());
            final var unionEntry = sortedUnionCasesReference.get(randomIndex);
            final var unionCase = unionEntry.getKey();
            final var unionData = unionEntry.getValue();

            return Map.of(unionCase,
                    _UStruct.constructRandomStruct(unionData.fields, new HashMap<>(), includeRandomOptionalFields,
                            typeParameters, randomGenerator));
        }
    }

    static Map.Entry<String, Object> entry(Map<String, Object> union) {
        return union.entrySet().stream().findAny().orElse(null);
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        return "Object";
    }
}
