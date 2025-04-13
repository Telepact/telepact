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

import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { TType } from '../types/TType';

export class ParseContext {
    public readonly documentName: string;
    public readonly telepactSchemaDocumentNamesToPseudoJson: { [key: string]: any[] };
    public readonly telepactSchemaDocumentNamesToJson: { [key: string]: string };
    public readonly schemaKeysToDocumentName: { [key: string]: string };
    public readonly schemaKeysToIndex: { [key: string]: number };
    public readonly parsedTypes: { [key: string]: TType };
    public readonly fnErrorRegexes: { [key: string]: string };
    public readonly allParseFailures: SchemaParseFailure[];
    public readonly failedTypes: Set<string>;

    constructor(
        documentName: string,
        telepactSchemaDocumentNamesToPseudoJson: { [key: string]: any[] },
        telepactSchemaDocumentNamesToJson: { [key: string]: string },
        schemaKeysToDocumentName: { [key: string]: string },
        schemaKeysToIndex: { [key: string]: number },
        parsedTypes: { [key: string]: TType },
        fnErrorRegexes: { [key: string]: string },
        allParseFailures: SchemaParseFailure[],
        failedTypes: Set<string>
    ) {
        this.documentName = documentName;
        this.telepactSchemaDocumentNamesToPseudoJson = telepactSchemaDocumentNamesToPseudoJson;
        this.telepactSchemaDocumentNamesToJson = telepactSchemaDocumentNamesToJson;
        this.schemaKeysToDocumentName = schemaKeysToDocumentName;
        this.schemaKeysToIndex = schemaKeysToIndex;
        this.parsedTypes = parsedTypes;
        this.fnErrorRegexes = fnErrorRegexes;
        this.allParseFailures = allParseFailures;
        this.failedTypes = failedTypes;
    }

    public copy({ documentName }: { documentName?: string }): ParseContext {
        return new ParseContext(
            documentName ?? this.documentName,
            this.telepactSchemaDocumentNamesToPseudoJson,
            this.telepactSchemaDocumentNamesToJson,
            this.schemaKeysToDocumentName,
            this.schemaKeysToIndex,
            this.parsedTypes,
            this.fnErrorRegexes,
            this.allParseFailures,
            this.failedTypes
        );
    }
}
