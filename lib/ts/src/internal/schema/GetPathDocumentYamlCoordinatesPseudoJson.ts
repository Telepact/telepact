//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { createDocumentLocatorFromYamlText } from './BuildDocumentLocatorFromYamlAst.js';
import { Coordinates, DocumentLocator, Path } from './DocumentLocators.js';

export function createPathDocumentYamlCoordinatesPseudoJsonLocator(text: string): DocumentLocator {
    return createDocumentLocatorFromYamlText(text);
}

export function getPathDocumentYamlCoordinatesPseudoJson(path: Path, document: string): Coordinates {
    return createPathDocumentYamlCoordinatesPseudoJsonLocator(document)(path);
}
