export class SchemaParseFailure {
    documentName: string;
    path: any[];
    reason: string;
    data: Record<string, any>;
    key: string | null;

    constructor(documentName: string, path: any[], reason: string, data: Record<string, any>) {
        this.documentName = documentName;
        this.path = path;
        this.reason = reason;
        this.data = data;
    }
}
