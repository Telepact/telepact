import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { UType } from '../../internal/types/UType';

export class ParseContext {
    public readonly documentName: string;
    public readonly path: any[];
    public readonly uapiSchemaDocumentNamesToPseudoJson: { [key: string]: any[] };
    public readonly schemaKeysToDocumentName: { [key: string]: string };
    public readonly schemaKeysToIndex: { [key: string]: number };
    public readonly parsedTypes: { [key: string]: UType };
    public readonly allParseFailures: SchemaParseFailure[];
    public readonly failedTypes: Set<string>;

    constructor(
        documentName: string,
        path: any[],
        uapiSchemaDocumentNamesToPseudoJson: { [key: string]: any[] },
        schemaKeysToDocumentName: { [key: string]: string },
        schemaKeysToIndex: { [key: string]: number },
        parsedTypes: { [key: string]: UType },
        allParseFailures: SchemaParseFailure[],
        failedTypes: Set<string>,
    ) {
        this.documentName = documentName;
        this.path = path;
        this.uapiSchemaDocumentNamesToPseudoJson = uapiSchemaDocumentNamesToPseudoJson;
        this.schemaKeysToDocumentName = schemaKeysToDocumentName;
        this.schemaKeysToIndex = schemaKeysToIndex;
        this.parsedTypes = parsedTypes;
        this.allParseFailures = allParseFailures;
        this.failedTypes = failedTypes;
    }

    public copy({ documentName, path }: { documentName?: string; path?: any[] }): ParseContext {
        return new ParseContext(
            documentName ?? this.documentName,
            path ?? this.path,
            this.uapiSchemaDocumentNamesToPseudoJson,
            this.schemaKeysToDocumentName,
            this.schemaKeysToIndex,
            this.parsedTypes,
            this.allParseFailures,
            this.failedTypes,
        );
    }
}
