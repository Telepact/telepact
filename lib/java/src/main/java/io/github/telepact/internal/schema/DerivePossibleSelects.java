//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

package io.github.telepact.internal.schema;

import java.util.*;

import io.github.telepact.internal.types.TFieldDeclaration;
import io.github.telepact.internal.types.TStruct;
import io.github.telepact.internal.types.TType;
import io.github.telepact.internal.types.TUnion;

public class DerivePossibleSelects {

    public static Map<String, Object> derivePossibleSelect(String fnName, TUnion result) {
        final var nestedTypes = new HashMap<String, TType>();
        final var okFields = result.tags.get("Ok_").fields;

        final var okFieldNames = new ArrayList<>(okFields.keySet());
        Collections.sort(okFieldNames);

        findNestedTypes(okFields, nestedTypes);

        final var possibleSelect = new HashMap<String, Object>();

        possibleSelect.put("->", Collections.singletonMap("Ok_", okFieldNames));

        final var sortedTypeKeys = new ArrayList<>(nestedTypes.keySet());
        Collections.sort(sortedTypeKeys);
        for (final var k : sortedTypeKeys) {
            final var v = nestedTypes.get(k);
            if (v instanceof TUnion u) {
                final var unionSelect = new HashMap<String, List<String>>();
                final var sortedTagKeys = new ArrayList<>(u.tags.keySet());
                Collections.sort(sortedTagKeys);
                for (final var c : sortedTagKeys) {
                    final var typ = u.tags.get(c);
                    final var selectedFieldNames = new ArrayList<String>();
                    final var sortedFieldNames = new ArrayList<>(typ.fields.keySet());
                    Collections.sort(sortedFieldNames);
                    selectedFieldNames.addAll(sortedFieldNames);

                    unionSelect.put(c, selectedFieldNames);
                }

                possibleSelect.put(k, unionSelect);
            } else if (v instanceof TStruct s) {
                final var structSelect = new ArrayList<String>();
                final var sortedFieldNames = new ArrayList<>(s.fields.keySet());
                Collections.sort(sortedFieldNames);
                structSelect.addAll(sortedFieldNames);

                possibleSelect.put(k, structSelect);
            }
        }

        return possibleSelect;
    }

    private static void findNestedTypes(Map<String, TFieldDeclaration> fields, Map<String, TType> nestedTypes) {
        for (final var field : fields.values()) {
            final var typ = field.typeDeclaration.type;
            if (typ instanceof TUnion u) {
                nestedTypes.put(u.name, typ);
                for (final var c : u.tags.values()) {
                    findNestedTypes(c.fields, nestedTypes);
                }
            } else if (typ instanceof TStruct s) {
                nestedTypes.put(s.name, typ);
                findNestedTypes(s.fields, nestedTypes);
            }
        }
    }
}
