//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { getPathDocumentCoordinatesPseudoJson } from './GetPathDocumentCoordinatesPseudoJson.js';

export type Path = (string | number)[];
export type Coordinates = { row: number; col: number };
export type DocumentLocator = (path: Path) => Coordinates;

const DOCUMENT_LOCATORS = Symbol('telepactDocumentLocators');

type DocumentMapWithLocators = Record<string, string> & {
    [DOCUMENT_LOCATORS]?: Record<string, DocumentLocator>;
};

export function setDocumentLocators(
    documentNamesToJson: Record<string, string>,
    documentLocators: Record<string, DocumentLocator>,
): void {
    Object.defineProperty(documentNamesToJson, DOCUMENT_LOCATORS, {
        configurable: true,
        enumerable: false,
        value: { ...documentLocators },
        writable: true,
    });
}

export function getDocumentLocators(
    documentNamesToJson: Record<string, string>,
): Record<string, DocumentLocator> | undefined {
    return (documentNamesToJson as DocumentMapWithLocators)[DOCUMENT_LOCATORS];
}

export function copyDocumentLocators(
    src: Record<string, string>,
    dst: Record<string, string>,
): void {
    const srcLocators = getDocumentLocators(src);
    if (srcLocators !== undefined) {
        setDocumentLocators(dst, srcLocators);
    }
}

export function resolveDocumentCoordinates(
    path: Path,
    documentName: string,
    documentNamesToJson: Record<string, string>,
): Coordinates {
    const documentLocators = getDocumentLocators(documentNamesToJson);
    const locator = documentLocators?.[documentName];
    if (locator !== undefined) {
        return locator(path);
    }

    const document = documentNamesToJson[documentName] ?? '[]';
    return getPathDocumentCoordinatesPseudoJson(path, document);
}
