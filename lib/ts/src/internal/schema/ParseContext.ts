import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { VType } from '../types/VType';

export class ParseContext {
    public readonly documentName: string;
    public readonly telepactSchemaDocumentNamesToPseudoJson: { [key: string]: any[] };
    public readonly telepactSchemaDocumentNamesToJson: { [key: string]: string };
    public readonly schemaKeysToDocumentName: { [key: string]: string };
    public readonly schemaKeysToIndex: { [key: string]: number };
    public readonly parsedTypes: { [key: string]: VType };
    public readonly allParseFailures: SchemaParseFailure[];
    public readonly failedTypes: Set<string>;

    constructor(
        documentName: string,
        telepactSchemaDocumentNamesToPseudoJson: { [key: string]: any[] },
        telepactSchemaDocumentNamesToJson: { [key: string]: string },
        schemaKeysToDocumentName: { [key: string]: string },
        schemaKeysToIndex: { [key: string]: number },
        parsedTypes: { [key: string]: VType },
        allParseFailures: SchemaParseFailure[],
        failedTypes: Set<string>,
    ) {
        this.documentName = documentName;
        this.telepactSchemaDocumentNamesToPseudoJson = telepactSchemaDocumentNamesToPseudoJson;
        this.telepactSchemaDocumentNamesToJson = telepactSchemaDocumentNamesToJson;
        this.schemaKeysToDocumentName = schemaKeysToDocumentName;
        this.schemaKeysToIndex = schemaKeysToIndex;
        this.parsedTypes = parsedTypes;
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
            this.allParseFailures,
            this.failedTypes,
        );
    }
}
