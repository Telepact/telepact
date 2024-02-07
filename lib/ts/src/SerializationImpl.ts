/**
 * A serialization implementation that converts between pseudo-JSON Objects and
 * byte array JSON payloads.
 * 
 * Pseudo-JSON objects are defined as data structures that represent JSON
 * objects as Maps and JSON arrays as Lists.
 */
export interface SerializationImpl {
    toJson(message: any): Promise<Uint8Array>;
    toMsgPack(message: any): Promise<Uint8Array>;
    fromJson(bytes: Uint8Array): Promise<any>;
    fromMsgPack(bytes: Uint8Array): Promise<any>;
}
