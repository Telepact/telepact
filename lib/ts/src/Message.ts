import { unionEntry } from "./_util";


/**
 * A uAPI Message.
 */
export class Message {
    constructor(public readonly header: Record<string, any>, public readonly body: Record<string, any>) {}

    public getBodyTarget(): string {
        const entry = unionEntry(this.body);
        return entry[0];
    }

    public getBodyPayload(): Map<string, any> {
        const entry = unionEntry(this.body);
        return entry[1];
    }
}