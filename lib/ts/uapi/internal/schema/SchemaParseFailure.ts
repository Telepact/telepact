export class SchemaParseFailure {
    path: object[];
    reason: string;
    data: Record<string, any>;
    key: string | null;

    constructor(path: object[], reason: string, data: Record<string, any>, key: string | null) {
        this.path = path;
        this.reason = reason;
        this.data = data;
        this.key = key;
    }
}
