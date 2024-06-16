export class Message {
    constructor(
        private header: Record<string, any>,
        private body: Record<string, any>,
    ) {}

    getBodyTarget(): string {
        const entry = Object.entries(this.body)[0];
        return entry[0];
    }

    getBodyPayload(): Record<string, any> {
        const entry = Object.entries(this.body)[0];
        return entry[1] as Record<string, any>;
    }
}
