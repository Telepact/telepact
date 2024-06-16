export interface Serialization {
    /**
     * A serialization implementation that converts between pseudo-JSON Objects and
     * byte array JSON payloads.
     *
     * Pseudo-JSON objects are defined as data structures that represent JSON
     * objects as dicts and JSON arrays as lists.
     */

    toJson(message: any): Uint8Array;

    toMsgpack(message: any): Uint8Array;

    fromJson(bytes: Uint8Array): any;

    fromMsgpack(bytes: Uint8Array): any;
}
