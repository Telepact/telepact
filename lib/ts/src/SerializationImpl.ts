/**
 * A serialization implementation that converts between pseudo-JSON Objects and
 * byte array JSON payloads.
 *
 * Pseudo-JSON objects are defined as data structures that represent JSON
 * objects as Maps and JSON arrays as Lists.
 */
export interface SerializationImpl {
    toJson(uapiMessage: any): Uint8Array;
    toMsgPack(uapiMessage: any): Uint8Array;
    fromJson(bytes: Uint8Array): any;
    fromMsgPack(bytes: Uint8Array): any;
}
