export class Response {
    constructor(public body: Uint8Array, public headers: Record<string, any>) {}
}