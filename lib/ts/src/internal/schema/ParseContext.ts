import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { VType } from '../types/VType';

export class ParseContext {
    public readonly documentName: string;
    public readonly msgpactSchemaDocumentNamesToPseudoJson: { [key: string]: any[] };
    public readonly msgpactSchemaDocumentNamesToJson: { [key: string]: string };
    public readonly schemaKeysToDocumentName: { [key: string]: string };
    public readonly schemaKeysToIndex: { [key: string]: number };
    public readonly parsedTypes: { [key: string]: VType };
    public readonly allParseFailures: SchemaParseFailure[];
    public readonly failedTypes: Set<string>;

    constructor(
        documentName: string,
        msgpactSchemaDocumentNamesToPseudoJson: { [key: string]: any[] },
        msgpactSchemaDocumentNamesToJson: { [key: string]: string },
        schemaKeysToDocumentName: { [key: string]: string },
        schemaKeysToIndex: { [key: string]: number },
        parsedTypes: { [key: string]: VType },
        allParseFailures: SchemaParseFailure[],
        failedTypes: Set<string>,
    ) {
        this.documentName = documentName;
        this.msgpactSchemaDocumentNamesToPseudoJson = msgpactSchemaDocumentNamesToPseudoJson;
        this.msgpactSchemaDocumentNamesToJson = msgpactSchemaDocumentNamesToJson;
        this.schemaKeysToDocumentName = schemaKeysToDocumentName;
        this.schemaKeysToIndex = schemaKeysToIndex;
        this.parsedTypes = parsedTypes;
        this.allParseFailures = allParseFailures;
        this.failedTypes = failedTypes;
    }

    public copy({ documentName }: { documentName?: string }): ParseContext {
        return new ParseContext(
            documentName ?? this.documentName,
            this.msgpactSchemaDocumentNamesToPseudoJson,
            this.msgpactSchemaDocumentNamesToJson,
            this.schemaKeysToDocumentName,
            this.schemaKeysToIndex,
            this.parsedTypes,
            this.allParseFailures,
            this.failedTypes,
        );
    }
}
