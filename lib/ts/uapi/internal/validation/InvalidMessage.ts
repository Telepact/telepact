export class InvalidMessage extends Error {
    constructor(cause?: Error) {
        super('Invalid message', {cause: cause});
    }
}
