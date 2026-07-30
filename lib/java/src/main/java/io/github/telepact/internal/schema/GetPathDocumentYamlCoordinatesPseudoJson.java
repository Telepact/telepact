//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.schema;

import java.util.List;
import java.util.Map;

import io.github.telepact.internal.schema.DocumentLocators.DocumentLocator;

public class GetPathDocumentYamlCoordinatesPseudoJson {

    public static DocumentLocator createPathDocumentYamlCoordinatesPseudoJsonLocator(String text) throws Exception {
        return BuildDocumentLocatorFromYamlAst.createDocumentLocatorFromYamlText(text);
    }

    public static Map<String, Object> getPathDocumentYamlCoordinatesPseudoJson(List<Object> path, String document)
            throws Exception {
        return createPathDocumentYamlCoordinatesPseudoJsonLocator(document).locate(path);
    }
}
