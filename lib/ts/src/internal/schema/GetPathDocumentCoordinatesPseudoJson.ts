//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { createDocumentLocatorFromYamlText } from './BuildDocumentLocatorFromYamlAst.js';
import { Coordinates, Path } from './DocumentLocators.js';

export function getPathDocumentCoordinatesPseudoJson(path: Path, document: string): Coordinates {
    try {
        return createDocumentLocatorFromYamlText(document)(path);
    } catch {
        return { row: 1, col: 1 };
    }
}
