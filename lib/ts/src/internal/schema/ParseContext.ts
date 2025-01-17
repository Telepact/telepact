import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { UType } from '../../internal/types/UType';

export class ParseContext {
    public readonly documentName: string;
    public readonly uapiSchemaDocumentNamesToPseudoJson: { [key: string]: any[] };
    public readonly uapiSchemaDocumentNamesToJson: { [key: string]: string };
    public readonly schemaKeysToDocumentName: { [key: string]: string };
    public readonly schemaKeysToIndex: { [key: string]: number };
    public readonly parsedTypes: { [key: string]: UType };
    public readonly allParseFailures: SchemaParseFailure[];
    public readonly failedTypes: Set<string>;

    constructor(
        documentName: string,
        uapiSchemaDocumentNamesToPseudoJson: { [key: string]: any[] },
        uapiSchemaDocumentNamesToJson: { [key: string]: string },
        schemaKeysToDocumentName: { [key: string]: string },
        schemaKeysToIndex: { [key: string]: number },
        parsedTypes: { [key: string]: UType },
        allParseFailures: SchemaParseFailure[],
        failedTypes: Set<string>,
    ) {
        this.documentName = documentName;
        this.uapiSchemaDocumentNamesToPseudoJson = uapiSchemaDocumentNamesToPseudoJson;
        this.uapiSchemaDocumentNamesToJson = uapiSchemaDocumentNamesToJson;
        this.schemaKeysToDocumentName = schemaKeysToDocumentName;
        this.schemaKeysToIndex = schemaKeysToIndex;
        this.parsedTypes = parsedTypes;
        this.allParseFailures = allParseFailures;
        this.failedTypes = failedTypes;
    }

    public copy({ documentName }: { documentName?: string }): ParseContext {
        return new ParseContext(
            documentName ?? this.documentName,
            this.uapiSchemaDocumentNamesToPseudoJson,
            this.uapiSchemaDocumentNamesToJson,
            this.schemaKeysToDocumentName,
            this.schemaKeysToIndex,
            this.parsedTypes,
            this.allParseFailures,
            this.failedTypes,
        );
    }
}
