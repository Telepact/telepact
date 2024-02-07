/**
 * Indicates failure to serialize a uAPI Message.
 */
export class SerializationError extends Error {
    constructor(cause: Error) {
        super(cause.message);
        Object.setPrototypeOf(this, SerializationError.prototype);
    }
}