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

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

import io.github.telepact.TelepactSchemaParseError;

public class FindSchemaKey {

    public static String findSchemaKey(String documentName, Map<String, Object> definition, int index,
            Map<String, String> documentNamesToJson) {
        final var regex = "^(((fn|errors|headers|info)|((struct|union|_ext)(<[0-2]>)?))\\..*)";
        final var matches = new ArrayList<String>();

        final var keys = definition.keySet().stream().sorted().toList();

        for (final var e : keys) {
            if (e.matches(regex)) {
                matches.add(e);
            }
        }

        if (matches.size() == 1) {
            return matches.get(0);
        } else {
            final var parseFailure = new SchemaParseFailure(documentName, List.of(index),
                    "ObjectKeyRegexMatchCountUnexpected",
                    new TreeMap<>(
                            Map.of("regex", regex, "actual", matches.size(), "expected", 1, "keys", keys)));
            throw new TelepactSchemaParseError(List.of(parseFailure), documentNamesToJson);
        }
    }
}
