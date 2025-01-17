package uapi.internal.schema;

import java.util.*;

import uapi.internal.types.UFieldDeclaration;
import uapi.internal.types.UStruct;
import uapi.internal.types.UType;
import uapi.internal.types.UUnion;

public class DerivePossibleSelects {

    public static Map<String, Object> derivePossibleSelect(String fnName, UUnion result) {
        final var nestedTypes = new HashMap<String, UType>();
        final var okFields = result.cases.get("Ok_").fields;

        final var okFieldNames = new ArrayList<>(okFields.keySet());
        Collections.sort(okFieldNames);

        findNestedTypes(okFields, nestedTypes);

        final var possibleSelect = new HashMap<String, Object>();

        possibleSelect.put("->", Collections.singletonMap("Ok_", okFieldNames));

        final var sortedTypeKeys = new ArrayList<>(nestedTypes.keySet());
        Collections.sort(sortedTypeKeys);
        for (final var k : sortedTypeKeys) {
            System.out.println("k: " + k);
            final var v = nestedTypes.get(k);
            if (v instanceof UUnion u) {
                final var unionSelect = new HashMap<String, List<String>>();
                final var sortedCaseKeys = new ArrayList<>(u.cases.keySet());
                Collections.sort(sortedCaseKeys);
                for (final var c : sortedCaseKeys) {
                    final var typ = u.cases.get(c);
                    final var selectedFieldNames = new ArrayList<String>();
                    final var sortedFieldNames = new ArrayList<>(typ.fields.keySet());
                    Collections.sort(sortedFieldNames);
                    selectedFieldNames.addAll(sortedFieldNames);

                    unionSelect.put(c, selectedFieldNames);
                }

                possibleSelect.put(k, unionSelect);
            } else if (v instanceof UStruct s) {
                final var structSelect = new ArrayList<String>();
                final var sortedFieldNames = new ArrayList<>(s.fields.keySet());
                Collections.sort(sortedFieldNames);
                structSelect.addAll(sortedFieldNames);

                possibleSelect.put(k, structSelect);
            }
        }

        return possibleSelect;
    }

    private static void findNestedTypes(Map<String, UFieldDeclaration> fields, Map<String, UType> nestedTypes) {
        for (final var field : fields.values()) {
            final var typ = field.typeDeclaration.type;
            if (typ instanceof UUnion u) {
                nestedTypes.put(u.name, typ);
                for (final var c : u.cases.values()) {
                    findNestedTypes(c.fields, nestedTypes);
                }
            } else if (typ instanceof UStruct s) {
                nestedTypes.put(s.name, typ);
                findNestedTypes(s.fields, nestedTypes);
            }
        }
    }
}
