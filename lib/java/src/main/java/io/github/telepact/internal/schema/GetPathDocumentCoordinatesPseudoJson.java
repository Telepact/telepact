//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.schema;

import java.util.List;
import java.util.Map;

public class GetPathDocumentCoordinatesPseudoJson {

    public static Map<String, Object> getPathDocumentCoordinatesPseudoJson(List<Object> path, String document) {
        try {
            return BuildDocumentLocatorFromYamlAst.createDocumentLocatorFromYamlText(document).locate(path);
        } catch (Exception e) {
            return Map.of("row", 1, "col", 1);
        }
    }
}
