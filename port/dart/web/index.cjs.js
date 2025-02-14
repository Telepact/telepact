'use strict';

var msgpackr = require('msgpackr');
var crc32 = require('crc-32');

/*
 * For debeugging.
 */
class RandomGenerator {
    seed;
    collectionLengthMin;
    collectionLengthMax;
    count = 0;
    constructor(collectionLengthMin, collectionLengthMax) {
        this.setSeed(0);
        this.collectionLengthMin = collectionLengthMin;
        this.collectionLengthMax = collectionLengthMax;
    }
    setSeed(seed) {
        this.seed = seed === 0 ? 1 : seed;
    }
    nextInt() {
        let x = this.seed;
        x ^= x << 16;
        x ^= x >> 11;
        x ^= x << 5;
        this.seed = x === 0 ? 1 : x;
        this.count += 1;
        const result = this.seed;
        // console.log(`${this.count} ${result} ${findStack()}`);
        return result & 0x7fffffff;
    }
    nextIntWithCeiling(ceiling) {
        if (ceiling === 0) {
            return 0;
        }
        return this.nextInt() % ceiling;
    }
    nextBoolean() {
        return this.nextIntWithCeiling(31) > 15;
    }
    nextString() {
        const buffer = new ArrayBuffer(4);
        const view = new DataView(buffer);
        view.setInt32(0, this.nextInt());
        const byteArray = new Uint8Array(buffer);
        const base64String = btoa(String.fromCharCode.apply(null, byteArray));
        return base64String.replace(/=/g, '');
    }
    nextDouble() {
        return (this.nextInt() & 0x7fffffff) / 0x7fffffff;
    }
    nextCollectionLength() {
        return this.nextIntWithCeiling(this.collectionLengthMax - this.collectionLengthMin) + this.collectionLengthMin;
    }
}

class Checksum {
    value;
    expiration;
    constructor(value, expiration) {
        this.value = value;
        this.expiration = expiration;
    }
}
class DefaultClientBinaryStrategy {
    primary = null;
    secondary = null;
    lastUpdate = new Date();
    updateChecksum(newChecksum) {
        if (!this.primary) {
            this.primary = new Checksum(newChecksum, 0);
            return;
        }
        if (this.primary.value !== newChecksum) {
            this.secondary = this.primary;
            this.primary = new Checksum(newChecksum, 0);
            if (this.secondary) {
                this.secondary.expiration += 1;
            }
            return;
        }
        this.lastUpdate = new Date();
    }
    getCurrentChecksums() {
        if (!this.primary) {
            return [];
        }
        else if (!this.secondary) {
            return [this.primary.value];
        }
        else {
            const minutesSinceLastUpdate = (Date.now() - this.lastUpdate.getTime()) / (1000 * 60);
            // Every 10 minute interval of non-use is a penalty point
            const penalty = Math.floor(minutesSinceLastUpdate / 10) + 1;
            if (this.secondary) {
                this.secondary.expiration += 1 * penalty;
            }
            if (this.secondary && this.secondary.expiration > 5) {
                this.secondary = null;
                return [this.primary.value];
            }
            else {
                return [this.primary.value, this.secondary.value];
            }
        }
    }
}

class DefaultSerialization {
    packr = new msgpackr.Packr({ mapsAsObjects: false, useRecords: false });
    unpackr = new msgpackr.Unpackr({ mapsAsObjects: false, useRecords: false });
    toJson(uapiMessage) {
        const jsonStr = JSON.stringify(uapiMessage);
        return new TextEncoder().encode(jsonStr);
    }
    toMsgpack(uapiMessage) {
        return this.packr.encode(uapiMessage);
    }
    fromJson(bytes) {
        const jsonStr = new TextDecoder().decode(bytes);
        return JSON.parse(jsonStr);
    }
    fromMsgpack(bytes) {
        return this.unpackr.decode(bytes);
    }
}

class SerializationError extends Error {
    constructor(cause) {
        super(cause.message);
        Object.setPrototypeOf(this, SerializationError.prototype);
    }
}

function serializeInternal(message, binaryEncoder, serializer) {
    const headers = message.headers;
    let serializeAsBinary;
    if ('_binary' in headers) {
        serializeAsBinary = headers['_binary'] === true;
        delete headers['_binary'];
    }
    else {
        serializeAsBinary = false;
    }
    const messageAsPseudoJson = [message.headers, message.body];
    try {
        if (serializeAsBinary) {
            try {
                const encodedMessage = binaryEncoder.encode(messageAsPseudoJson);
                return serializer.toMsgpack(encodedMessage);
            }
            catch (error) {
                // We can still submit as JSON
                return serializer.toJson(messageAsPseudoJson);
            }
        }
        else {
            return serializer.toJson(messageAsPseudoJson);
        }
    }
    catch (error) {
        throw new SerializationError(error);
    }
}

class Message {
    headers;
    body;
    constructor(headers, body) {
        this.headers = headers;
        this.body = body;
    }
    getBodyTarget() {
        const entry = Object.entries(this.body)[0];
        return entry[0];
    }
    getBodyPayload() {
        const entry = Object.entries(this.body)[0];
        return entry[1];
    }
}

class InvalidMessage extends Error {
    constructor(cause) {
        super('Invalid message', { cause: cause });
    }
}

class InvalidMessageBody extends Error {
}

function deserializeInternal(messageBytes, serializer, binaryEncoder) {
    let messageAsPseudoJson;
    let isMsgPack;
    try {
        if (messageBytes[0] === 0x92) {
            // MsgPack
            isMsgPack = true;
            messageAsPseudoJson = serializer.fromMsgpack(messageBytes);
        }
        else {
            isMsgPack = false;
            messageAsPseudoJson = serializer.fromJson(messageBytes);
        }
    }
    catch (e) {
        throw new InvalidMessage();
    }
    if (!Array.isArray(messageAsPseudoJson)) {
        throw new InvalidMessage();
    }
    const messageAsPseudoJsonList = messageAsPseudoJson;
    if (messageAsPseudoJsonList.length !== 2) {
        throw new InvalidMessage();
    }
    let finalMessageAsPseudoJsonList;
    if (isMsgPack) {
        finalMessageAsPseudoJsonList = binaryEncoder.decode(messageAsPseudoJsonList);
    }
    else {
        finalMessageAsPseudoJsonList = messageAsPseudoJsonList;
    }
    if (typeof finalMessageAsPseudoJsonList[0] !== 'object' || Array.isArray(finalMessageAsPseudoJsonList[0])) {
        throw new InvalidMessage();
    }
    const headers = finalMessageAsPseudoJsonList[0];
    if (typeof finalMessageAsPseudoJsonList[1] !== 'object' || Array.isArray(finalMessageAsPseudoJsonList[1])) {
        throw new InvalidMessage();
    }
    const body = finalMessageAsPseudoJsonList[1];
    if (Object.keys(body).length !== 1) {
        throw new InvalidMessageBody();
    }
    if (typeof Object.values(body)[0] !== 'object' || Array.isArray(Object.values(body)[0])) {
        throw new InvalidMessageBody();
    }
    return new Message(headers, body);
}

class Serializer {
    /**
     * A serializer that converts a Message to and from a serialized form.
     */
    serializationImpl;
    binaryEncoder;
    constructor(serializationImpl, binaryEncoder) {
        this.serializationImpl = serializationImpl;
        this.binaryEncoder = binaryEncoder;
    }
    serialize(message) {
        /**
         * Serialize a Message into a byte array.
         */
        return serializeInternal(message, this.binaryEncoder, this.serializationImpl);
    }
    deserialize(messageBytes) {
        /**
         * Deserialize a Message from a byte array.
         */
        return deserializeInternal(messageBytes, this.serializationImpl, this.binaryEncoder);
    }
}

class BinaryEncoderUnavailableError extends Error {
}

function encodeKeys(given, binaryEncoder) {
    if (given === null || given === undefined) {
        return given;
    }
    else if (typeof given === 'object' && !Array.isArray(given)) {
        const newMap = new Map();
        for (const [key, value] of Object.entries(given)) {
            const finalKey = binaryEncoder.encodeMap.has(key) ? binaryEncoder.encodeMap.get(key) : key;
            const encodedValue = encodeKeys(value, binaryEncoder);
            newMap.set(finalKey, encodedValue);
        }
        return newMap;
    }
    else if (Array.isArray(given)) {
        return given.map((value) => encodeKeys(value, binaryEncoder));
    }
    else {
        return given;
    }
}

function encodeBody(messageBody, binaryEncoder) {
    return encodeKeys(messageBody, binaryEncoder);
}

class BinaryPackNode {
    value;
    nested;
    constructor(value, nested) {
        this.value = value;
        this.nested = nested;
    }
}

class CannotPack extends Error {
    constructor(message) {
        super(message);
        Object.setPrototypeOf(this, new.target.prototype);
    }
}

const UNDEFINED_BYTE = 18;
class MsgpackUndefined {
    toString() {
        return 'UNDEFINED';
    }
}
const MSGPACK_UNDEFINED_EXT = {
    Class: MsgpackUndefined,
    type: UNDEFINED_BYTE,
    pack(instance) {
        return Buffer.from([]);
    },
    unpack(buffer) {
        return new MsgpackUndefined();
    },
};
msgpackr.addExtension(MSGPACK_UNDEFINED_EXT);
function packMap(m, header, keyIndexMap) {
    const row = [];
    for (const [key, value] of m.entries()) {
        if (typeof key === 'string') {
            throw new CannotPack();
        }
        const keyIndex = keyIndexMap.get(key);
        let finalKeyIndex;
        if (keyIndex === undefined) {
            finalKeyIndex = new BinaryPackNode(header.length - 1, new Map());
            if (value instanceof Map) {
                header.push([key]);
            }
            else {
                header.push(key);
            }
            keyIndexMap.set(key, finalKeyIndex);
        }
        else {
            finalKeyIndex = keyIndex;
        }
        const keyIndexValue = finalKeyIndex.value;
        const keyIndexNested = finalKeyIndex.nested;
        let packedValue;
        if (value instanceof Map && value !== null) {
            const nestedHeader = header[keyIndexValue + 1];
            if (!Array.isArray(nestedHeader)) {
                // No nesting available, so the data structure is inconsistent
                throw new CannotPack();
            }
            packedValue = packMap(value, nestedHeader, keyIndexNested);
        }
        else {
            if (Array.isArray(header[keyIndexValue + 1])) {
                throw new CannotPack();
            }
            packedValue = pack(value);
        }
        while (row.length < keyIndexValue) {
            row.push(new MsgpackUndefined());
        }
        if (row.length === keyIndexValue) {
            row.push(packedValue);
        }
        else {
            row[keyIndexValue] = packedValue;
        }
    }
    return row;
}

const PACKED_BYTE = 17;
class MsgpackPacked {
    toString() {
        return 'PACKED';
    }
}
const MSGPACK_PACKED_EXT = {
    Class: MsgpackPacked,
    type: PACKED_BYTE,
    pack(instance) {
        return Buffer.from([]);
    },
    unpack(buffer) {
        return new MsgpackPacked();
    },
};
msgpackr.addExtension(MSGPACK_PACKED_EXT);
function packList(list) {
    if (list.length === 0) {
        return list;
    }
    const packedList = [];
    const header = [];
    packedList.push(new MsgpackPacked());
    header.push(null);
    packedList.push(header);
    const keyIndexMap = new Map();
    try {
        for (const e of list) {
            if (e instanceof Map) {
                const row = packMap(e, header, keyIndexMap);
                packedList.push(row);
            }
            else {
                // This list cannot be packed, abort
                throw new CannotPack();
            }
        }
        return packedList;
    }
    catch (ex) {
        const newList = [];
        for (const e of list) {
            newList.push(pack(e));
        }
        return newList;
    }
}

function pack(value) {
    if (Array.isArray(value)) {
        return packList(value);
    }
    else if (value instanceof Map) {
        const newMap = new Map();
        for (const [key, val] of value.entries()) {
            newMap.set(key, pack(val));
        }
        return newMap;
    }
    else {
        return value;
    }
}

function packBody(body) {
    const result = new Map();
    for (const [key, value] of body.entries()) {
        const packedValue = pack(value);
        result.set(key, packedValue);
    }
    return result;
}

function clientBinaryEncode(message, recentBinaryEncoders, binaryChecksumStrategy) {
    const headers = message[0];
    const messageBody = message[1];
    const forceSendJson = headers["_forceSendJson"];
    headers["bin_"] = binaryChecksumStrategy.getCurrentChecksums();
    if (forceSendJson === true) {
        throw new BinaryEncoderUnavailableError();
    }
    if (recentBinaryEncoders.size > 1) {
        throw new BinaryEncoderUnavailableError();
    }
    const binaryEncoder = [...recentBinaryEncoders.values()][0];
    if (!binaryEncoder) {
        throw new BinaryEncoderUnavailableError();
    }
    const encodedMessageBody = encodeBody(messageBody, binaryEncoder);
    let finalEncodedMessageBody;
    if (headers["pac_"] === true) {
        finalEncodedMessageBody = packBody(encodedMessageBody);
    }
    else {
        finalEncodedMessageBody = encodedMessageBody;
    }
    return [headers, finalEncodedMessageBody];
}

class BinaryEncoding {
    encodeMap;
    decodeMap;
    checksum;
    constructor(binaryEncodingMap, checksum) {
        this.encodeMap = binaryEncodingMap;
        const decodeList = [...binaryEncodingMap.entries()].map((e) => [
            e[1],
            e[0],
        ]);
        this.decodeMap = new Map(decodeList);
        this.checksum = checksum;
    }
}

class BinaryEncodingMissing extends Error {
    constructor(key) {
        super(`Missing binary encoding for ${String(key)}`);
    }
}

function decodeKeys(given, binaryEncoder) {
    if (given instanceof Map) {
        const newMap = {};
        for (const [key, value] of given.entries()) {
            const finalKey = typeof key === 'string' ? key : binaryEncoder.decodeMap.get(key);
            if (finalKey === undefined) {
                throw new BinaryEncodingMissing(key);
            }
            const decodedValue = decodeKeys(value, binaryEncoder);
            newMap[finalKey] = decodedValue;
        }
        return newMap;
    }
    else if (Array.isArray(given)) {
        return given.map((value) => decodeKeys(value, binaryEncoder));
    }
    else {
        return given;
    }
}

function decodeBody(encodedMessageBody, binaryEncoder) {
    return decodeKeys(encodedMessageBody, binaryEncoder);
}

function unpackMap(row, header) {
    const finalMap = new Map();
    for (let j = 0; j < row.length; j += 1) {
        const key = header[j + 1];
        const value = row[j];
        if (value instanceof MsgpackUndefined) {
            continue;
        }
        if (Array.isArray(key)) {
            const nestedHeader = key;
            const nestedRow = value;
            const m = unpackMap(nestedRow, nestedHeader);
            const i = nestedHeader[0];
            finalMap.set(i, m);
        }
        else {
            const unpackedValue = unpack(value);
            finalMap.set(key, unpackedValue);
        }
    }
    return finalMap;
}

function unpackList(list) {
    if (list.length === 0) {
        return list;
    }
    if (!(list[0] instanceof MsgpackPacked)) {
        const newList = [];
        for (const e of list) {
            newList.push(unpack(e));
        }
        return newList;
    }
    const unpackedList = [];
    const headers = list[1];
    for (let i = 2; i < list.length; i += 1) {
        const row = list[i];
        const m = unpackMap(row, headers);
        unpackedList.push(m);
    }
    return unpackedList;
}

function unpack(value) {
    if (Array.isArray(value)) {
        return unpackList(value);
    }
    else if (value instanceof Map) {
        const newMap = new Map();
        for (const [key, val] of value.entries()) {
            newMap.set(key, unpack(val));
        }
        return newMap;
    }
    else {
        return value;
    }
}

function unpackBody(body) {
    const result = new Map();
    for (const [key, value] of body.entries()) {
        const unpackedValue = unpack(value);
        result.set(key, unpackedValue);
    }
    return result;
}

function convertMapsToObjects(value) {
    if (value instanceof Map) {
        const newObj = {};
        for (const [key, val] of value.entries()) {
            newObj[key] = convertMapsToObjects(val);
        }
        return newObj;
    }
    else if (Array.isArray(value)) {
        const newList = [];
        for (const val of value) {
            const newVal = convertMapsToObjects(val);
            newList.push(newVal);
        }
        return newList;
    }
    else if (typeof value == 'object' && value !== null) {
        for (const [key, val] of Object.entries(value)) {
            convertMapsToObjects(val);
        }
    }
    else {
        return value;
    }
}

function clientBinaryDecode(message, recentBinaryEncoders, binaryChecksumStrategy) {
    const headers = message[0];
    const encodedMessageBody = message[1];
    const binaryChecksums = headers.get("bin_");
    const binaryChecksum = binaryChecksums[0];
    if (headers.has("enc_")) {
        const binaryEncoding = headers.get("enc_");
        const newBinaryEncoder = new BinaryEncoding(binaryEncoding, binaryChecksum);
        recentBinaryEncoders.set(binaryChecksum, newBinaryEncoder);
    }
    binaryChecksumStrategy.updateChecksum(binaryChecksum);
    const newCurrentChecksumStrategy = binaryChecksumStrategy.getCurrentChecksums();
    for (const [key, value] of recentBinaryEncoders) {
        if (!newCurrentChecksumStrategy.includes(key)) {
            recentBinaryEncoders.delete(key);
        }
    }
    const binaryEncoder = recentBinaryEncoders.get(binaryChecksum);
    let finalEncodedMessageBody;
    if (headers.get("pac_") === true) {
        finalEncodedMessageBody = unpackBody(encodedMessageBody);
    }
    else {
        finalEncodedMessageBody = encodedMessageBody;
    }
    const messageHeader = convertMapsToObjects(headers);
    const messageBody = decodeBody(finalEncodedMessageBody, binaryEncoder);
    return [messageHeader, messageBody];
}

class ClientBinaryEncoder {
    recentBinaryEncoders;
    binaryChecksumStrategy;
    constructor(binaryChecksumStrategy) {
        this.recentBinaryEncoders = new Map();
        this.binaryChecksumStrategy = binaryChecksumStrategy;
    }
    encode(message) {
        return clientBinaryEncode(message, this.recentBinaryEncoders, this.binaryChecksumStrategy);
    }
    decode(message) {
        return clientBinaryDecode(message, this.recentBinaryEncoders, this.binaryChecksumStrategy);
    }
}

class UApiError extends Error {
    constructor(arg) {
        super(typeof arg === 'string' ? arg : arg.message);
        if (typeof arg !== 'string') {
            this.stack = arg.stack;
        }
    }
}

function objectsAreEqual(obj1, obj2) {
    // Check if both objects are the same type
    if (typeof obj1 !== typeof obj2) {
        return false;
    }
    // If objects are primitive types, compare directly
    if (typeof obj1 !== 'object' || obj1 === null || obj2 === null) {
        return obj1 === obj2;
    }
    // Check if both objects have the same keys
    const keys1 = Object.keys(obj1);
    const keys2 = Object.keys(obj2);
    if (keys1.length !== keys2.length || !keys1.every((key) => keys2.includes(key))) {
        return false;
    }
    // Recursively compare nested objects and arrays
    for (const key of keys1) {
        if (!objectsAreEqual(obj1[key], obj2[key])) {
            return false;
        }
    }
    // If all checks pass, objects are considered equal
    return true;
}

function timeoutPromise(timeoutMs) {
    return new Promise((_resolve, reject) => {
        setTimeout(() => {
            reject(new Error('Promise timed out'));
        }, timeoutMs);
    });
}
async function processRequestObject(requestMessage, adapter, serializer, timeoutMsDefault, useBinaryDefault, alwaysSendJson) {
    const header = requestMessage.headers;
    try {
        if (!header.hasOwnProperty('time_')) {
            header['time_'] = timeoutMsDefault;
        }
        if (useBinaryDefault) {
            header['_binary'] = true;
        }
        if (header['_binary'] && alwaysSendJson) {
            header['_forceSendJson'] = true;
        }
        const timeoutMs = header['time_'];
        const responseMessage = await Promise.race([adapter(requestMessage, serializer), timeoutPromise(timeoutMs)]);
        if (objectsAreEqual(responseMessage.body, {
            ErrorParseFailure_: { reasons: [{ IncompatibleBinaryEncoding: {} }] },
        })) {
            header['_binary'] = true;
            header['_forceSendJson'] = true;
            return await Promise.race([adapter(requestMessage, serializer), timeoutPromise(timeoutMs)]);
        }
        return responseMessage;
    }
    catch (e) {
        throw new UApiError(e);
    }
}

class Client {
    adapter;
    useBinaryDefault;
    alwaysSendJson;
    timeoutMsDefault;
    serializer;
    constructor(adapter, options) {
        this.adapter = adapter;
        this.useBinaryDefault = options.useBinary;
        this.alwaysSendJson = options.alwaysSendJson;
        this.timeoutMsDefault = options.timeoutMsDefault;
        this.serializer = new Serializer(options.serializationImpl, new ClientBinaryEncoder(options.binaryStrategy));
    }
    async request(requestMessage) {
        return await processRequestObject(requestMessage, this.adapter, this.serializer, this.timeoutMsDefault, this.useBinaryDefault, this.alwaysSendJson);
    }
}
class ClientOptions {
    useBinary;
    alwaysSendJson;
    timeoutMsDefault;
    serializationImpl;
    binaryStrategy;
    constructor() {
        this.useBinary = false;
        this.alwaysSendJson = true;
        this.timeoutMsDefault = 5000;
        this.serializationImpl = new DefaultSerialization();
        this.binaryStrategy = new DefaultClientBinaryStrategy();
    }
}

function serverBinaryEncode(message, binaryEncoder) {
    const headers = message[0];
    const messageBody = message[1];
    const clientKnownBinaryChecksums = headers['_clientKnownBinaryChecksums'];
    delete headers['_clientKnownBinaryChecksums'];
    const resultTag = Object.keys(messageBody)[0];
    if (resultTag !== 'Ok_') {
        throw new BinaryEncoderUnavailableError();
    }
    if (clientKnownBinaryChecksums === undefined || !clientKnownBinaryChecksums.includes(binaryEncoder.checksum)) {
        headers['enc_'] = binaryEncoder.encodeMap;
    }
    headers['bin_'] = [binaryEncoder.checksum];
    const encodedMessageBody = encodeBody(messageBody, binaryEncoder);
    let finalEncodedMessageBody;
    if (headers['pac_'] === true) {
        finalEncodedMessageBody = packBody(encodedMessageBody);
    }
    else {
        finalEncodedMessageBody = encodedMessageBody;
    }
    return [headers, finalEncodedMessageBody];
}

function serverBinaryDecode(message, binaryEncoder) {
    const headers = message[0];
    const encodedMessageBody = message[1];
    const clientKnownBinaryChecksums = headers.get("bin_");
    const binaryChecksumUsedByClientOnThisMessage = clientKnownBinaryChecksums[0];
    if (binaryChecksumUsedByClientOnThisMessage !== binaryEncoder.checksum) {
        throw new BinaryEncoderUnavailableError();
    }
    let finalEncodedMessageBody;
    if (headers.get("pac_") === true) {
        finalEncodedMessageBody = unpackBody(encodedMessageBody);
    }
    else {
        finalEncodedMessageBody = encodedMessageBody;
    }
    const messageHeader = convertMapsToObjects(headers);
    const messageBody = decodeBody(finalEncodedMessageBody, binaryEncoder);
    return [messageHeader, messageBody];
}

class ServerBinaryEncoder {
    binaryEncoder;
    constructor(binaryEncoder) {
        this.binaryEncoder = binaryEncoder;
    }
    encode(message) {
        return serverBinaryEncode(message, this.binaryEncoder);
    }
    decode(message) {
        return serverBinaryDecode(message, this.binaryEncoder);
    }
}

function createChecksum(value) {
    const checksum = crc32.str(value);
    return checksum | 0;
}

class ValidationFailure {
    path;
    reason;
    data;
    constructor(path, reason, data) {
        this.path = path;
        this.reason = reason;
        this.data = data;
    }
}

function getType(value) {
    if (value === null) {
        return 'Null';
    }
    else if (typeof value === 'boolean') {
        return 'Boolean';
    }
    else if (typeof value === 'number') {
        return 'Number';
    }
    else if (typeof value === 'string') {
        return 'String';
    }
    else if (Array.isArray(value)) {
        return 'Array';
    }
    else if (typeof value === 'object') {
        return 'Object';
    }
    else {
        return 'Unknown';
    }
}

function getTypeUnexpectedValidationFailure(path, value, expectedType) {
    const actualType = getType(value);
    const data = {
        actual: { [actualType]: {} },
        expected: { [expectedType]: {} },
    };
    return [new ValidationFailure(path, 'TypeUnexpected', data)];
}

function validateStructFields(fields, selectedFields, actualStruct, ctx) {
    const validationFailures = [];
    const missingFields = [];
    for (const [fieldName, fieldDeclaration] of Object.entries(fields)) {
        const isOptional = fieldDeclaration.optional;
        const isOmittedBySelect = selectedFields !== null && !selectedFields.includes(fieldName);
        if (!(fieldName in actualStruct) && !isOptional && !isOmittedBySelect) {
            missingFields.push(fieldName);
        }
    }
    for (const missingField of missingFields) {
        const validationFailure = new ValidationFailure([], 'RequiredObjectKeyMissing', {
            key: missingField,
        });
        validationFailures.push(validationFailure);
    }
    for (const [fieldName, fieldValue] of Object.entries(actualStruct)) {
        const referenceField = fields[fieldName];
        if (referenceField === undefined) {
            const validationFailure = new ValidationFailure([fieldName], 'ObjectKeyDisallowed', {});
            validationFailures.push(validationFailure);
            continue;
        }
        const refFieldTypeDeclaration = referenceField.typeDeclaration;
        const nestedValidationFailures = refFieldTypeDeclaration.validate(fieldValue, ctx);
        const nestedValidationFailuresWithPath = [];
        for (const failure of nestedValidationFailures) {
            const thisPath = [fieldName, ...failure.path];
            nestedValidationFailuresWithPath.push(new ValidationFailure(thisPath, failure.reason, failure.data));
        }
        validationFailures.push(...nestedValidationFailuresWithPath);
    }
    return validationFailures;
}

function validateUnionStruct(unionStruct, unionTag, actual, selectedTags, ctx) {
    const selectedFields = selectedTags?.[unionTag] ?? null;
    return validateStructFields(unionStruct.fields, selectedFields, actual, ctx);
}

function validateUnionTags(referenceTags, selectedTags, actual, ctx) {
    if (Object.keys(actual).length !== 1) {
        return [
            new ValidationFailure([], "ObjectSizeUnexpected", {
                actual: Object.keys(actual).length,
                expected: 1,
            }),
        ];
    }
    const [unionTarget, unionPayload] = Object.entries(actual)[0];
    const referenceStruct = referenceTags[unionTarget];
    if (referenceStruct === undefined) {
        return [new ValidationFailure([unionTarget], "ObjectKeyDisallowed", {})];
    }
    if (typeof unionPayload === "object" && !Array.isArray(unionPayload)) {
        const nestedValidationFailures = validateUnionStruct(referenceStruct, unionTarget, unionPayload, selectedTags, ctx);
        const nestedValidationFailuresWithPath = [];
        for (const failure of nestedValidationFailures) {
            const thisPath = [unionTarget, ...failure.path];
            nestedValidationFailuresWithPath.push(new ValidationFailure(thisPath, failure.reason, failure.data));
        }
        return nestedValidationFailuresWithPath;
    }
    else {
        return getTypeUnexpectedValidationFailure([unionTarget], unionPayload, "Object");
    }
}

function validateUnion(value, name, tags, ctx) {
    if (typeof value === "object" && !Array.isArray(value)) {
        let selectedTags;
        if (name.startsWith("fn.")) {
            selectedTags = { [name]: ctx.select?.[name] ?? null };
        }
        else {
            selectedTags = ctx.select?.[name] ?? null;
        }
        return validateUnionTags(tags, selectedTags, value, ctx);
    }
    else {
        return getTypeUnexpectedValidationFailure([], value, unionName);
    }
}

function generateRandomStruct(blueprintValue, useBlueprintValue, referenceStruct, ctx) {
    const startingStruct = useBlueprintValue ? blueprintValue : {};
    const sortedReferenceStruct = Array.from(Object.entries(referenceStruct)).sort((e1, e2) => {
        const a = e1[0];
        const b = e2[0];
        for (let i = 0; i < Math.min(a.length, b.length); i++) {
            const charCodeA = a.charCodeAt(i);
            const charCodeB = b.charCodeAt(i);
            if (charCodeA !== charCodeB) {
                // If the characters are different, return the comparison result
                // where lowercase letters are considered greater than uppercase letters
                return charCodeA - charCodeB;
            }
        }
        // If one string is a prefix of the other, the shorter string comes first
        return a.length - b.length;
    });
    const obj = {};
    for (const [fieldName, fieldDeclaration] of sortedReferenceStruct) {
        const thisBlueprintValue = startingStruct[fieldName];
        const thisUseBlueprintValue = fieldName in startingStruct;
        const typeDeclaration = fieldDeclaration.typeDeclaration;
        let value;
        if (thisUseBlueprintValue) {
            value = typeDeclaration.generateRandomValue(thisBlueprintValue, thisUseBlueprintValue, ctx);
        }
        else {
            if (!fieldDeclaration.optional) {
                if (!ctx.alwaysIncludeRequiredFields && ctx.randomGenerator.nextBoolean()) {
                    continue;
                }
                value = typeDeclaration.generateRandomValue(null, false, ctx);
            }
            else {
                if (!ctx.includeOptionalFields || (ctx.randomizeOptionalFields && ctx.randomGenerator.nextBoolean())) {
                    continue;
                }
                value = typeDeclaration.generateRandomValue(null, false, ctx);
            }
        }
        obj[fieldName] = value;
    }
    return obj;
}

function generateRandomUnion(blueprintValue, useBlueprintValue, unionTagsReference, ctx) {
    if (!useBlueprintValue) {
        const sortedUnionTagsReference = Object.entries(unionTagsReference).sort((a, b) => a[0].localeCompare(b[0]));
        const randomIndex = ctx.randomGenerator.nextIntWithCeiling(sortedUnionTagsReference.length);
        const [unionTag, unionData] = sortedUnionTagsReference[randomIndex];
        return {
            [unionTag]: generateRandomStruct(null, false, unionData.fields, ctx),
        };
    }
    else {
        const startingUnion = blueprintValue;
        const [unionTag, unionStartingStruct] = Object.entries(startingUnion)[0];
        const unionStructType = unionTagsReference[unionTag];
        return {
            [unionTag]: generateRandomStruct(unionStartingStruct, true, unionStructType.fields, ctx),
        };
    }
}

const unionName = "Object";
class UUnion {
    name;
    tags;
    tagIndices;
    constructor(name, tags, tagIndices) {
        this.name = name;
        this.tags = tags;
        this.tagIndices = tagIndices;
    }
    getTypeParameterCount() {
        return 0;
    }
    validate(value, typeParameters, ctx) {
        return validateUnion(value, this.name, this.tags, ctx);
    }
    generateRandomValue(blueprintValue, useBlueprintValue, typeParameters, ctx) {
        return generateRandomUnion(blueprintValue, useBlueprintValue, this.tags, ctx);
    }
    getName() {
        return unionName;
    }
}

function validateStruct(value, name, fields, ctx) {
    if (typeof value === 'object' && !Array.isArray(value)) {
        const selectedFields = ctx.select?.[name] ?? null;
        return validateStructFields(fields, selectedFields, value, ctx);
    }
    else {
        return getTypeUnexpectedValidationFailure([], value, structName);
    }
}

const structName = 'Object';
class UStruct {
    name;
    fields;
    constructor(name, fields) {
        this.name = name;
        this.fields = fields;
    }
    getTypeParameterCount() {
        return 0;
    }
    validate(value, typeParameters, ctx) {
        return validateStruct(value, this.name, this.fields, ctx);
    }
    generateRandomValue(blueprintValue, useBlueprintValue, typeParameters, ctx) {
        return generateRandomStruct(blueprintValue, useBlueprintValue, this.fields, ctx);
    }
    getName() {
        return structName;
    }
}

class UType {
}

const FN_NAME = "Object";
class UFn extends UType {
    name;
    call;
    result;
    errorsRegex;
    inheritedErrors = [];
    constructor(name, call, output, errorsRegex) {
        super();
        this.name = name;
        this.call = call;
        this.result = output;
        this.errorsRegex = errorsRegex;
    }
    getTypeParameterCount() {
        return 0;
    }
    validate(value, typeParameters, ctx) {
        return this.call.validate(value, [], ctx);
    }
    generateRandomValue(blueprintValue, useBlueprintValue, typeParameters, ctx) {
        return generateRandomUnion(blueprintValue, useBlueprintValue, this.call.tags, ctx);
    }
    getName() {
        return FN_NAME;
    }
}

function constructBinaryEncoding(uApiSchema) {
    const allKeys = new Set();
    for (const [key, value] of Object.entries(uApiSchema.parsed)) {
        allKeys.add(key);
        if (value instanceof UStruct) {
            const structFields = value.fields;
            for (const structFieldKey of Object.keys(structFields)) {
                allKeys.add(structFieldKey);
            }
        }
        else if (value instanceof UUnion) {
            const unionTags = value.tags;
            for (const [tagKey, tagValue] of Object.entries(unionTags)) {
                allKeys.add(tagKey);
                const structFields = tagValue.fields;
                for (const structFieldKey of Object.keys(structFields)) {
                    allKeys.add(structFieldKey);
                }
            }
        }
        else if (value instanceof UFn) {
            const fnCallTags = value.call.tags;
            const fnResultTags = value.result.tags;
            for (const [tagKey, tagValue] of Object.entries(fnCallTags)) {
                allKeys.add(tagKey);
                const structFields = tagValue.fields;
                for (const structFieldKey of Object.keys(structFields)) {
                    allKeys.add(structFieldKey);
                }
            }
            for (const [tagKey, tagValue] of Object.entries(fnResultTags)) {
                allKeys.add(tagKey);
                const structFields = tagValue.fields;
                for (const structFieldKey of Object.keys(structFields)) {
                    allKeys.add(structFieldKey);
                }
            }
        }
    }
    const sortedAllKeys = Array.from(allKeys).sort();
    const binaryEncoding = new Map();
    sortedAllKeys.forEach((key, index) => {
        binaryEncoding.set(key, index);
    });
    const finalString = sortedAllKeys.join("\n");
    const checksum = createChecksum(finalString);
    return new BinaryEncoding(binaryEncoding, checksum);
}

function validateValueOfType(value, thisType, nullable, typeParameters, ctx) {
    if (value === null) {
        if (!nullable) {
            return getTypeUnexpectedValidationFailure([], value, thisType.getName());
        }
        else {
            return [];
        }
    }
    return thisType.validate(value, typeParameters, ctx);
}

function generateRandomValueOfType(blueprintValue, useBlueprintValue, thisType, nullable, typeParameters, ctx) {
    if (nullable && !useBlueprintValue && ctx.randomGenerator.nextBoolean()) {
        return null;
    }
    else {
        return thisType.generateRandomValue(blueprintValue, useBlueprintValue, typeParameters, ctx);
    }
}

class UTypeDeclaration {
    type;
    nullable;
    typeParameters;
    constructor(type, nullable, typeParameters) {
        this.type = type;
        this.nullable = nullable;
        this.typeParameters = typeParameters;
    }
    validate(value, ctx) {
        return validateValueOfType(value, this.type, this.nullable, this.typeParameters, ctx);
    }
    generateRandomValue(blueprintValue, useBlueprintValue, ctx) {
        return generateRandomValueOfType(blueprintValue, useBlueprintValue, this.type, this.nullable, this.typeParameters, ctx);
    }
}

function validateArray(value, typeParameters, ctx) {
    if (Array.isArray(value)) {
        const nestedTypeDeclaration = typeParameters[0];
        const validationFailures = [];
        for (let i = 0; i < value.length; i++) {
            const element = value[i];
            const nestedValidationFailures = nestedTypeDeclaration.validate(element, ctx);
            const index = i;
            const nestedValidationFailuresWithPath = [];
            for (const f of nestedValidationFailures) {
                const finalPath = [index, ...f.path];
                nestedValidationFailuresWithPath.push(new ValidationFailure(finalPath, f.reason, f.data));
            }
            validationFailures.push(...nestedValidationFailuresWithPath);
        }
        return validationFailures;
    }
    else {
        return getTypeUnexpectedValidationFailure([], value, arrayName);
    }
}

function generateRandomArray(blueprintValue, useBlueprintValue, typeParameters, ctx) {
    const nestedTypeDeclaration = typeParameters[0];
    if (useBlueprintValue) {
        const startingArray = blueprintValue;
        const array = [];
        for (const startingArrayValue of startingArray) {
            const value = nestedTypeDeclaration.generateRandomValue(startingArrayValue, useBlueprintValue, ctx);
            array.push(value);
        }
        return array;
    }
    else {
        const length = ctx.randomGenerator.nextCollectionLength();
        const array = [];
        for (let i = 0; i < length; i++) {
            const value = nestedTypeDeclaration.generateRandomValue(null, false, ctx);
            array.push(value);
        }
        return array;
    }
}

const arrayName = 'Array';
class UArray extends UType {
    getTypeParameterCount() {
        return 1;
    }
    validate(value, typeParameters, ctx) {
        return validateArray(value, typeParameters, ctx);
    }
    generateRandomValue(blueprintValue, useBlueprintValue, typeParameters, ctx) {
        return generateRandomArray(blueprintValue, useBlueprintValue, typeParameters, ctx);
    }
    getName() {
        return arrayName;
    }
}

function validateObject(value, typeParameters, ctx) {
    if (typeof value === 'object' && !Array.isArray(value)) {
        const nestedTypeDeclaration = typeParameters[0];
        const validationFailures = [];
        for (const [k, v] of Object.entries(value)) {
            const nestedValidationFailures = nestedTypeDeclaration.validate(v, ctx);
            const nestedValidationFailuresWithPath = [];
            for (const f of nestedValidationFailures) {
                const thisPath = [k, ...f.path];
                nestedValidationFailuresWithPath.push(new ValidationFailure(thisPath, f.reason, f.data));
            }
            validationFailures.push(...nestedValidationFailuresWithPath);
        }
        return validationFailures;
    }
    else {
        return getTypeUnexpectedValidationFailure([], value, objectName);
    }
}

function generateRandomObject(blueprintValue, useBlueprintValue, typeParameters, ctx) {
    const nestedTypeDeclaration = typeParameters[0];
    if (useBlueprintValue) {
        const startingObj = blueprintValue;
        const obj = {};
        for (const [key, startingObjValue] of Object.entries(startingObj)) {
            const value = nestedTypeDeclaration.generateRandomValue(startingObjValue, true, ctx);
            obj[key] = value;
        }
        return obj;
    }
    else {
        const length = ctx.randomGenerator.nextCollectionLength();
        const obj = {};
        for (let i = 0; i < length; i++) {
            const key = ctx.randomGenerator.nextString();
            const value = nestedTypeDeclaration.generateRandomValue(null, false, ctx);
            obj[key] = value;
        }
        return obj;
    }
}

const objectName = 'Object';
class UObject {
    getTypeParameterCount() {
        return 1;
    }
    validate(value, typeParameters, ctx) {
        return validateObject(value, typeParameters, ctx);
    }
    generateRandomValue(blueprintValue, useBlueprintValue, typeParameters, ctx) {
        return generateRandomObject(blueprintValue, useBlueprintValue, typeParameters, ctx);
    }
    getName() {
        return objectName;
    }
}

function selectStructFields(typeDeclaration, value, selectedStructFields) {
    const typeDeclarationType = typeDeclaration.type;
    const typeDeclarationTypeParams = typeDeclaration.typeParameters;
    if (typeDeclarationType instanceof UStruct) {
        const fields = typeDeclarationType.fields;
        const structName = typeDeclarationType.name;
        const selectedFields = selectedStructFields[structName];
        const valueAsMap = value;
        const finalMap = {};
        for (const [fieldName, fieldValue] of Object.entries(valueAsMap)) {
            if (selectedFields === undefined || selectedFields.includes(fieldName)) {
                const field = fields[fieldName];
                const fieldTypeDeclaration = field.typeDeclaration;
                const valueWithSelectedFields = selectStructFields(fieldTypeDeclaration, fieldValue, selectedStructFields);
                finalMap[fieldName] = valueWithSelectedFields;
            }
        }
        return finalMap;
    }
    else if (typeDeclarationType instanceof UFn) {
        const valueAsMap = value;
        const [unionTag, unionData] = Object.entries(valueAsMap)[0];
        const fnName = typeDeclarationType.name;
        const fnCall = typeDeclarationType.call;
        const fnCallTags = fnCall.tags;
        const argStructReference = fnCallTags[unionTag];
        const selectedFields = selectedStructFields[fnName];
        const finalMap = {};
        for (const [fieldName, fieldValue] of Object.entries(unionData)) {
            if (selectedFields === undefined || selectedFields.includes(fieldName)) {
                const field = argStructReference.fields[fieldName];
                const valueWithSelectedFields = selectStructFields(field.typeDeclaration, fieldValue, selectedStructFields);
                finalMap[fieldName] = valueWithSelectedFields;
            }
        }
        return { [unionTag]: finalMap };
    }
    else if (typeDeclarationType instanceof UUnion) {
        const valueAsMap = value;
        const [unionTag, unionData] = Object.entries(valueAsMap)[0];
        const unionTags = typeDeclarationType.tags;
        const unionStructReference = unionTags[unionTag];
        const unionStructRefFields = unionStructReference.fields;
        const defaultTagsToFields = {};
        for (const [tagName, unionStruct] of Object.entries(unionTags)) {
            const fieldNames = Object.keys(unionStruct.fields);
            defaultTagsToFields[tagName] = fieldNames;
        }
        const unionSelectedFields = selectedStructFields[typeDeclarationType.name];
        const thisUnionTagSelectedFieldsDefault = defaultTagsToFields[unionTag];
        const selectedFields = unionSelectedFields?.[unionTag] || thisUnionTagSelectedFieldsDefault;
        const finalMap = {};
        for (const [fieldName, fieldValue] of Object.entries(unionData)) {
            if (selectedFields === undefined || selectedFields.includes(fieldName)) {
                const field = unionStructRefFields[fieldName];
                const valueWithSelectedFields = selectStructFields(field.typeDeclaration, fieldValue, selectedStructFields);
                finalMap[fieldName] = valueWithSelectedFields;
            }
        }
        return { [unionTag]: finalMap };
    }
    else if (typeDeclarationType instanceof UObject) {
        const nestedTypeDeclaration = typeDeclarationTypeParams[0];
        const valueAsMap = value;
        const finalMap = {};
        for (const [key, value] of Object.entries(valueAsMap)) {
            const valueWithSelectedFields = selectStructFields(nestedTypeDeclaration, value, selectedStructFields);
            finalMap[key] = valueWithSelectedFields;
        }
        return finalMap;
    }
    else if (typeDeclarationType instanceof UArray) {
        const nestedType = typeDeclarationTypeParams[0];
        const valueAsList = value;
        const finalList = [];
        for (const entry of valueAsList) {
            const valueWithSelectedFields = selectStructFields(nestedType, entry, selectedStructFields);
            finalList.push(valueWithSelectedFields);
        }
        return finalList;
    }
    else {
        return value;
    }
}

function mapValidationFailuresToInvalidFieldCases(argumentValidationFailures) {
    const validationFailureCases = [];
    for (const validationFailure of argumentValidationFailures) {
        const validationFailureCase = {
            path: validationFailure.path,
            reason: { [validationFailure.reason]: validationFailure.data },
        };
        validationFailureCases.push(validationFailureCase);
    }
    return validationFailureCases;
}

class ValidateContext {
    select;
    fn;
    constructor(select, fn) {
        this.select = select;
        this.fn = fn;
    }
}

function validateResult(resultUnionType, errorResult) {
    const newErrorResultValidationFailures = resultUnionType.validate(errorResult, [], new ValidateContext(null, null));
    if (newErrorResultValidationFailures.length !== 0) {
        throw new UApiError(`Failed internal uAPI validation: ${JSON.stringify(mapValidationFailuresToInvalidFieldCases(newErrorResultValidationFailures))}`);
    }
}

function getInvalidErrorMessage(error, validationFailures, resultUnionType, responseHeaders) {
    const validationFailureCases = mapValidationFailuresToInvalidFieldCases(validationFailures);
    const newErrorResult = {
        [error]: {
            cases: validationFailureCases,
        },
    };
    validateResult(resultUnionType, newErrorResult);
    return new Message(responseHeaders, newErrorResult);
}

function validateHeaders(headers, parsedRequestHeaders, functionType) {
    const validationFailures = [];
    for (const header in headers) {
        const headerValue = headers[header];
        const field = parsedRequestHeaders[header];
        if (field) {
            const thisValidationFailures = field.typeDeclaration.validate(headerValue, new ValidateContext(null, functionType.name));
            const thisValidationFailuresPath = thisValidationFailures.map((e) => new ValidationFailure([header, ...e.path], e.reason, e.data));
            validationFailures.push(...thisValidationFailuresPath);
        }
    }
    return validationFailures;
}

async function handleMessage(requestMessage, uApiSchema, handler, onError) {
    const responseHeaders = {};
    const requestHeaders = requestMessage.headers;
    const requestBody = requestMessage.body;
    const parsedUApiSchema = uApiSchema.parsed;
    const requestEntry = Object.entries(requestBody)[0];
    const requestTargetInit = requestEntry[0];
    const requestPayload = requestEntry[1];
    let unknownTarget;
    let requestTarget;
    if (!(requestTargetInit in parsedUApiSchema)) {
        unknownTarget = requestTargetInit;
        requestTarget = 'fn.ping_';
    }
    else {
        unknownTarget = null;
        requestTarget = requestTargetInit;
    }
    const functionType = parsedUApiSchema[requestTarget];
    const resultUnionType = functionType.result;
    const callId = requestHeaders['id_'];
    if (callId !== undefined) {
        responseHeaders['id_'] = callId;
    }
    if ('_parseFailures' in requestHeaders) {
        const parseFailures = requestHeaders['_parseFailures'];
        const newErrorResult = {
            ErrorParseFailure_: { reasons: parseFailures },
        };
        validateResult(resultUnionType, newErrorResult);
        return new Message(responseHeaders, newErrorResult);
    }
    const requestHeaderValidationFailures = validateHeaders(requestHeaders, uApiSchema.parsedRequestHeaders, functionType);
    if (requestHeaderValidationFailures.length > 0) {
        return getInvalidErrorMessage('ErrorInvalidRequestHeaders_', requestHeaderValidationFailures, resultUnionType, responseHeaders);
    }
    if ('bin_' in requestHeaders) {
        const clientKnownBinaryChecksums = requestHeaders['bin_'];
        responseHeaders['_binary'] = true;
        responseHeaders['_clientKnownBinaryChecksums'] = clientKnownBinaryChecksums;
        if ('pac_' in requestHeaders) {
            responseHeaders['pac_'] = requestHeaders['pac_'];
        }
    }
    const selectStructFieldsHeader = requestHeaders['select_'] || null;
    if (unknownTarget !== null) {
        const newErrorResult = {
            ErrorInvalidRequestBody_: {
                cases: [
                    {
                        path: [unknownTarget],
                        reason: { FunctionUnknown: {} },
                    },
                ],
            },
        };
        validateResult(resultUnionType, newErrorResult);
        return new Message(responseHeaders, newErrorResult);
    }
    const functionTypeCall = functionType.call;
    const warnings = [];
    const filterOutWarnings = (e) => {
        const r = e.reason == 'NumberTruncated';
        if (r) {
            warnings.push(e);
        }
        return !r;
    };
    const callValidationFailures = functionTypeCall
        .validate(requestBody, [], new ValidateContext(null, functionType.name))
        .filter(filterOutWarnings);
    if (callValidationFailures.length > 0) {
        if (warnings.length > 0) {
            responseHeaders['_warnings'] = mapValidationFailuresToInvalidFieldCases(warnings);
        }
        return getInvalidErrorMessage('ErrorInvalidRequestBody_', callValidationFailures, resultUnionType, responseHeaders);
    }
    const unsafeResponseEnabled = requestHeaders['unsafe_'] || false;
    const callMessage = new Message(requestHeaders, { [requestTarget]: requestPayload });
    let resultMessage;
    if (requestTarget === 'fn.ping_') {
        resultMessage = new Message({}, { Ok_: {} });
    }
    else if (requestTarget === 'fn.api_') {
        resultMessage = new Message({}, { Ok_: { api: uApiSchema.original } });
    }
    else {
        try {
            resultMessage = await handler(callMessage);
        }
        catch (e) {
            try {
                onError(e);
            }
            catch (error) {
                // Ignore error
            }
            return new Message(responseHeaders, { ErrorUnknown_: {} });
        }
    }
    const resultUnion = resultMessage.body;
    resultMessage.headers = { ...resultMessage.headers, ...responseHeaders };
    const finalResponseHeaders = resultMessage.headers;
    const skipResultValidation = unsafeResponseEnabled;
    if (!skipResultValidation) {
        const resultValidationFailures = resultUnionType
            .validate(resultUnion, [], new ValidateContext(selectStructFieldsHeader, functionType.name))
            .filter(filterOutWarnings);
        if (warnings.length > 0) {
            responseHeaders['_warnings'] = mapValidationFailuresToInvalidFieldCases(warnings);
        }
        if (resultValidationFailures.length > 0) {
            return getInvalidErrorMessage('ErrorInvalidResponseBody_', resultValidationFailures, resultUnionType, responseHeaders);
        }
        const responseHeaderValidationFailures = validateHeaders(finalResponseHeaders, uApiSchema.parsedResponseHeaders, functionType);
        if (responseHeaderValidationFailures.length > 0) {
            return getInvalidErrorMessage('ErrorInvalidResponseHeaders_', responseHeaderValidationFailures, resultUnionType, responseHeaders);
        }
    }
    let finalResultUnion;
    if (selectStructFieldsHeader !== null) {
        finalResultUnion = selectStructFields(new UTypeDeclaration(resultUnionType, false, []), resultUnion, selectStructFieldsHeader);
    }
    else {
        finalResultUnion = resultUnion;
    }
    return new Message(finalResponseHeaders, finalResultUnion);
}

function parseRequestMessage(requestMessageBytes, serializer, uapiSchema, onError) {
    try {
        return serializer.deserialize(requestMessageBytes);
    }
    catch (e) {
        onError(e);
        let reason;
        if (e instanceof BinaryEncoderUnavailableError) {
            reason = 'IncompatibleBinaryEncoding';
        }
        else if (e instanceof BinaryEncodingMissing) {
            reason = 'BinaryDecodeFailure';
        }
        else if (e instanceof InvalidMessage) {
            reason = 'ExpectedJsonArrayOfTwoObjects';
        }
        else if (e instanceof InvalidMessageBody) {
            reason = 'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject';
        }
        else {
            reason = 'ExpectedJsonArrayOfTwoObjects';
        }
        return new Message({ _parseFailures: [{ [reason]: {} }] }, { _unknown: {} });
    }
}

async function processBytes(requestMessageBytes, serializer, uapiSchema, onError, onRequest, onResponse, handler) {
    try {
        const requestMessage = parseRequestMessage(requestMessageBytes, serializer, uapiSchema, onError);
        try {
            onRequest(requestMessage);
        }
        catch (error) {
            // Handle error
        }
        const responseMessage = await handleMessage(requestMessage, uapiSchema, handler, onError);
        try {
            onResponse(responseMessage);
        }
        catch (error) {
            // Handle error
        }
        return serializer.serialize(responseMessage);
    }
    catch (error) {
        try {
            onError(error);
        }
        catch (error) {
            // Handle error
        }
        return serializer.serialize(new Message({}, { ErrorUnknown_: {} }));
    }
}

class Server {
    handler;
    onError;
    onRequest;
    onResponse;
    uApiSchema;
    serializer;
    constructor(uApiSchema, handler, options) {
        this.handler = handler;
        this.onError = options.onError;
        this.onRequest = options.onRequest;
        this.onResponse = options.onResponse;
        this.uApiSchema = uApiSchema;
        const binaryEncoding = constructBinaryEncoding(this.uApiSchema);
        const binaryEncoder = new ServerBinaryEncoder(binaryEncoding);
        this.serializer = new Serializer(options.serialization, binaryEncoder);
        if (!('struct.Auth_' in this.uApiSchema.parsed) && options.authRequired) {
            throw new Error('Unauthenticated server. Either define a non-empty `struct._Auth` in your schema or set `options.authRequired` to `false`.');
        }
    }
    async process(requestMessageBytes) {
        return await processBytes(requestMessageBytes, this.serializer, this.uApiSchema, this.onError, this.onRequest, this.onResponse, this.handler);
    }
}
class ServerOptions {
    onError;
    onRequest;
    onResponse;
    authRequired;
    serialization;
    constructor() {
        this.onError = (e) => { };
        this.onRequest = (m) => { };
        this.onResponse = (m) => { };
        this.authRequired = true;
        this.serialization = new DefaultSerialization();
    }
}

var internalUApi = [
	{
		"///": " Ping the server. ",
		"fn.ping_": {
		},
		"->": [
			{
				Ok_: {
				}
			}
		],
		_errors: "^errors\\.Validation_$"
	},
	{
		"///": " Get the uAPI `schema` of this server. ",
		"fn.api_": {
		},
		"->": [
			{
				Ok_: {
					api: [
						"array",
						[
							"object",
							[
								"any"
							]
						]
					]
				}
			}
		],
		_errors: "^errors\\.Validation_$"
	},
	{
		"_ext.Select_": {
		}
	},
	{
		"///": " The `time_` header indicates the request timeout honored by the client. ",
		"headers.Time_": {
			time_: [
				"integer"
			]
		},
		"->": {
		}
	},
	{
		"///": [
			" If `unsafe_` is set to `true`, response validation by the server will be        ",
			" disabled. The server will the client-provided the value of `unsafe_` header in  ",
			" the response.                                                                   "
		],
		"headers.Unsafe_": {
			unsafe_: [
				"boolean"
			]
		},
		"->": {
			unsafe_: [
				"boolean"
			]
		}
	},
	{
		"///": " The `select_` header is used to select fields from structs. ",
		"headers.Select_": {
			select_: [
				"_ext.Select_"
			]
		},
		"->": {
		}
	},
	{
		"///": [
			" The `bin_` header indicates the valid checksums of binary encodings negotiated  ",
			" between the client and server. If the client sends a `bin_` header with any     ",
			" value, the server will respond with a `bin_` header with an array containing    ",
			" the currently supported binary encoding checksum. If the client's provided      ",
			" checksum does not match the server's checksum, the server will also send an     ",
			" `enc_` header containing the binary encoding, which is a map of field names to  ",
			" field ids. The response body may also be encoded in binary.                     ",
			"                                                                                 ",
			" The `pac_` header can also be used to indicate usage of 'packed' binary         ",
			" encoding strategy. If the client submits a `pac_` header with a `true` value,   ",
			" the server will respond with a `pac_` header with a `true` value.               "
		],
		"headers.Binary_": {
			bin_: [
				"array",
				[
					"integer"
				]
			],
			pac_: [
				"boolean"
			]
		},
		"->": {
			bin_: [
				"array",
				[
					"integer"
				]
			],
			enc_: [
				"object",
				[
					"integer"
				]
			],
			pac_: [
				"boolean"
			]
		}
	},
	{
		"///": " The `warn_` header is used to send warnings to the client. ",
		"headers.Warning_": {
		},
		"->": {
			warn_: [
				"array",
				[
					"string"
				]
			]
		}
	},
	{
		"///": [
			" The `id_` header is used to correlate requests and responses. The server will   ",
			" reflect the client-provided `id_` header as-is.                                 "
		],
		"headers.Id_": {
			id_: [
				"any"
			]
		},
		"->": {
			id_: [
				"any"
			]
		}
	},
	{
		"///": " A type. ",
		"union.Type_": [
			{
				Null: {
				}
			},
			{
				"Boolean": {
				}
			},
			{
				Integer: {
				}
			},
			{
				"Number": {
				}
			},
			{
				"String": {
				}
			},
			{
				"Array": {
				}
			},
			{
				"Object": {
				}
			},
			{
				Any: {
				}
			},
			{
				Unknown: {
				}
			}
		]
	},
	{
		"///": " A reason for the validation failure in the body. ",
		"union.ValidationFailureReason_": [
			{
				TypeUnexpected: {
					expected: [
						"union.Type_"
					],
					actual: [
						"union.Type_"
					]
				}
			},
			{
				NullDisallowed: {
				}
			},
			{
				ObjectKeyDisallowed: {
				}
			},
			{
				ArrayElementDisallowed: {
				}
			},
			{
				NumberOutOfRange: {
				}
			},
			{
				ObjectSizeUnexpected: {
					expected: [
						"integer"
					],
					actual: [
						"integer"
					]
				}
			},
			{
				ExtensionValidationFailed: {
					reason: [
						"string"
					],
					"data!": [
						"object",
						[
							"any"
						]
					]
				}
			},
			{
				ObjectKeyRegexMatchCountUnexpected: {
					regex: [
						"string"
					],
					expected: [
						"integer"
					],
					actual: [
						"integer"
					],
					keys: [
						"array",
						[
							"string"
						]
					]
				}
			},
			{
				RequiredObjectKeyMissing: {
					key: [
						"string"
					]
				}
			},
			{
				FunctionUnknown: {
				}
			}
		]
	},
	{
		"///": " A parse failure. ",
		"union.ParseFailure_": [
			{
				IncompatibleBinaryEncoding: {
				}
			},
			{
				"///": " The binary decoder encountered a field id that could not be mapped to a key. ",
				BinaryDecodeFailure: {
				}
			},
			{
				JsonInvalid: {
				}
			},
			{
				ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject: {
				}
			},
			{
				ExpectedJsonArrayOfTwoObjects: {
				}
			}
		]
	},
	{
		"///": " A validation failure located at a `path` explained by a `reason`. ",
		"struct.ValidationFailure_": {
			path: [
				"array",
				[
					"any"
				]
			],
			reason: [
				"union.ValidationFailureReason_"
			]
		}
	},
	{
		"///": " A standard error. ",
		"errors.Validation_": [
			{
				"///": " The server implementation raised an unknown error. ",
				ErrorUnknown_: {
				}
			},
			{
				"///": " The headers on the request are invalid. ",
				ErrorInvalidRequestHeaders_: {
					cases: [
						"array",
						[
							"struct.ValidationFailure_"
						]
					]
				}
			},
			{
				"///": " The body on the request is invalid. ",
				ErrorInvalidRequestBody_: {
					cases: [
						"array",
						[
							"struct.ValidationFailure_"
						]
					]
				}
			},
			{
				"///": " The headers on the response are invalid. ",
				ErrorInvalidResponseHeaders_: {
					cases: [
						"array",
						[
							"struct.ValidationFailure_"
						]
					]
				}
			},
			{
				"///": " The body that the server attempted to put on the response is invalid. ",
				ErrorInvalidResponseBody_: {
					cases: [
						"array",
						[
							"struct.ValidationFailure_"
						]
					]
				}
			},
			{
				"///": " The request could not be parsed as a uAPI Message. ",
				ErrorParseFailure_: {
					reasons: [
						"array",
						[
							"union.ParseFailure_"
						]
					]
				}
			}
		]
	}
];

function getInternalUApiJson() {
    return JSON.stringify(internalUApi);
}

var authUApi = [
	{
		"///": [
			" The `auth_` header is the conventional location for sending credentials to the  ",
			" server for the purpose of authentication and authorization.                     "
		],
		"headers.Auth_": {
			auth_: [
				"struct.Auth_"
			]
		},
		"->": {
		}
	},
	{
		"///": " A standard error. ",
		"errors.Auth_": [
			{
				"///": " The credentials in the `_auth` header were missing or invalid. ",
				ErrorUnauthenticated_: {
					"message!": [
						"string"
					]
				}
			},
			{
				"///": " The credentials in the `_auth` header were insufficient to run the function. ",
				ErrorUnauthorized_: {
					"message!": [
						"string"
					]
				}
			}
		]
	}
];

function getAuthUApiJson() {
    return JSON.stringify(authUApi);
}

class SchemaParseFailure {
    documentName;
    path;
    reason;
    data;
    key;
    constructor(documentName, path, reason, data) {
        this.documentName = documentName;
        this.path = path;
        this.reason = reason;
        this.data = data;
    }
}

class StringReader {
    s;
    index;
    row;
    col;
    constructor(s) {
        this.s = s;
        this.index = 0;
        this.row = 1;
        this.col = 0;
    }
    next() {
        if (this.index >= this.s.length) {
            return null;
        }
        const c = this.s[this.index++];
        if (c === '\n') {
            this.row += 1;
            this.col = 0;
        }
        else {
            this.col += 1;
        }
        console.log(`reader: char=${c}, row=${this.row}, col=${this.col}`);
        return [c, this.row, this.col];
    }
}
function getPathDocumentCoordinatesPseudoJson(path, document) {
    console.log(`getPathDocumentCoordinatesPseudoJson: path=${path}, document=${document}`);
    const reader = new StringReader(document);
    return findCoordinates(path, reader);
}
function findCoordinates(path, reader, ovRow, ovCol) {
    console.log(`findCoordinates: path=${path}`);
    let result;
    while ((result = reader.next()) !== null) {
        const [c, row, col] = result;
        if (path.length === 0) {
            return {
                row: ovRow ?? row,
                col: ovCol ?? col,
            };
        }
        console.log(`findCoordinates: char=${c}, row=${row}, col=${col}`);
        if (c === '{') {
            const result = findCoordinatesObject(path, reader);
            if (result) {
                return result;
            }
        }
        if (c === '[') {
            const result = findCoordinatesArray(path, reader);
            if (result) {
                return result;
            }
        }
    }
    throw new Error('findCoordinates: Path not found in document');
}
function findCoordinatesObject(path, reader) {
    console.log(`findCoordinatesObject: path=${path}`);
    let workingKeyRowStart = null;
    let workingKeyColStart = null;
    let workingKey;
    let result;
    while ((result = reader.next()) !== null) {
        const [c, row, col] = result;
        console.log(`findCoordinatesObject: char=${c}, row=${row}, col=${col}`);
        if (c === '}') {
            return null;
        }
        else if (c === '"') {
            workingKeyRowStart = row;
            workingKeyColStart = col;
            workingKey = findString(reader);
        }
        else if (c === ':') {
            if (workingKey === path[0]) {
                return findCoordinates(path.slice(1), reader, workingKeyRowStart, workingKeyColStart);
            }
            else {
                findValue(reader);
            }
        }
    }
    throw new Error('findCoordinatesObject: Path not found in document');
}
function findCoordinatesArray(path, reader) {
    console.log(`findCoordinatesArray: path=${path}`);
    let workingIndex = 0;
    if (workingIndex === path[0]) {
        return findCoordinates(path.slice(1), reader);
    }
    else {
        findValue(reader);
    }
    let result;
    while ((result = reader.next()) !== null) {
        const [c, row, col] = result;
        console.log(`findCoordinatesArray: char=${c}, row=${row}, col=${col}`);
        workingIndex += 1;
        console.log(`findCoordinatesArray: workingIndex=${workingIndex}`);
        if (workingIndex === path[0]) {
            return findCoordinates(path.slice(1), reader);
        }
        else {
            findValue(reader);
        }
    }
    throw new Error('findCoordinatesArray: Path not found in document');
}
function findValue(reader) {
    let result;
    while ((result = reader.next()) !== null) {
        const [c, row, col] = result;
        console.log(`findValue: char=${c}, row=${row}, col=${col}`);
        if (c === '{') {
            findObject(reader);
            return false;
        }
        else if (c === '[') {
            findArray(reader);
            return false;
        }
        else if (c === '"') {
            findString(reader);
            return false;
        }
        else if (c === '}') {
            return true;
        }
        else if (c === ']') {
            return true;
        }
        else if (c === ',') {
            return false;
        }
    }
    throw new Error('Value not found in document');
}
function findObject(reader) {
    let result;
    while ((result = reader.next()) !== null) {
        const [c, row, col] = result;
        console.log(`findObject: char=${c}, row=${row}, col=${col}`);
        if (c === '}') {
            return;
        }
        else if (c === '"') {
            findString(reader);
        }
        else if (c === ':') {
            if (findValue(reader)) {
                return;
            }
        }
    }
}
function findArray(reader) {
    console.log('findArray');
    if (findValue(reader)) {
        return;
    }
    let result;
    while ((result = reader.next()) !== null) {
        const [c, row, col] = result;
        console.log(`findArray: char=${c}, row=${row}, col=${col}`);
        if (c === ']') {
            return;
        }
        if (findValue(reader)) {
            return;
        }
    }
}
function findString(reader) {
    let workingString = '';
    let result;
    while ((result = reader.next()) !== null) {
        const [c, row, col] = result;
        console.log(`findString: char=${c}`);
        if (c === '"') {
            return workingString;
        }
        else {
            workingString += c;
        }
    }
    throw new Error('String not closed');
}

function mapSchemaParseFailuresToPseudoJson(schemaParseFailures, documentNamesToJson) {
    const pseudoJsonList = [];
    for (const f of schemaParseFailures) {
        const documentJson = documentNamesToJson[f.documentName];
        const location = getPathDocumentCoordinatesPseudoJson(f.path, documentJson);
        const pseudoJson = {};
        pseudoJson.document = f.documentName;
        pseudoJson.location = location;
        pseudoJson.path = f.path;
        pseudoJson.reason = { [f.reason]: f.data };
        pseudoJsonList.push(Object.assign({}, pseudoJson));
    }
    return pseudoJsonList;
}

class UApiSchemaParseError extends Error {
    /**
     * Indicates failure to parse a uAPI Schema.
     */
    schemaParseFailures;
    schemaParseFailuresPseudoJson;
    constructor(schemaParseFailures, documentNamesToJson, cause) {
        super(JSON.stringify(mapSchemaParseFailuresToPseudoJson(schemaParseFailures, documentNamesToJson), null, 2), {
            cause: cause,
        });
        this.schemaParseFailures = schemaParseFailures;
        this.schemaParseFailuresPseudoJson = mapSchemaParseFailuresToPseudoJson(schemaParseFailures, documentNamesToJson);
    }
}

function applyErrorToParsedTypes(error, parsedTypes, schemaKeysToDocumentNames, schemaKeysToIndex, documentNamesToJson) {
    const parseFailures = [];
    const errorKey = error.name;
    const errorIndex = schemaKeysToIndex[errorKey];
    const documentName = schemaKeysToDocumentNames[errorKey];
    for (const parsedTypeName in parsedTypes) {
        const parsedType = parsedTypes[parsedTypeName];
        if (!(parsedType instanceof UFn)) {
            continue;
        }
        const f = parsedType;
        const fnName = f.name;
        const regex = new RegExp(f.errorsRegex);
        const fnResult = f.result;
        const fnResultTags = fnResult.tags;
        const errorErrors = error.errors;
        const errorTags = errorErrors.tags;
        const matcher = regex.exec(errorKey);
        if (!matcher) {
            continue;
        }
        for (const errorTagName in errorTags) {
            const errorTag = errorTags[errorTagName];
            const newKey = errorTagName;
            if (newKey in fnResultTags) {
                const otherPathIndex = schemaKeysToIndex[fnName];
                const errorTagIndex = error.errors.tagIndices[newKey];
                const otherDocumentName = schemaKeysToDocumentNames[fnName];
                const fnErrorTagIndex = f.result.tagIndices[newKey];
                const otherPath = [otherPathIndex, "->", fnErrorTagIndex, newKey];
                const otherDocumentJson = documentNamesToJson[otherDocumentName];
                const otherLocation = getPathDocumentCoordinatesPseudoJson(otherPath, otherDocumentJson);
                parseFailures.push(new SchemaParseFailure(documentName, [errorIndex, errorKey, errorTagIndex, newKey], "PathCollision", { document: otherDocumentName, path: otherPath, location: otherLocation }));
            }
            fnResultTags[newKey] = errorTag;
        }
    }
    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures, documentNamesToJson);
    }
}

function catchErrorCollisions(uApiSchemaNameToPseudoJson, errorKeys, keysToIndex, schemaKeysToDocumentNames, documentNamesToJson) {
    const parseFailures = [];
    const errorKeysList = [...errorKeys];
    errorKeysList.sort((k1, k2) => {
        const documentName1 = schemaKeysToDocumentNames[k1];
        const documentName2 = schemaKeysToDocumentNames[k2];
        if (documentName1 !== documentName2) {
            return documentName1.localeCompare(documentName2);
        }
        else {
            const index1 = keysToIndex[k1];
            const index2 = keysToIndex[k2];
            return index1 - index2;
        }
    });
    for (let i = 0; i < errorKeysList.length; i++) {
        for (let j = i + 1; j < errorKeysList.length; j++) {
            const defKey = errorKeysList[i];
            const otherDefKey = errorKeysList[j];
            const index = keysToIndex[defKey];
            const otherIndex = keysToIndex[otherDefKey];
            const documentName = schemaKeysToDocumentNames[defKey];
            const otherDocumentName = schemaKeysToDocumentNames[otherDefKey];
            const uApiSchemaPseudoJson = uApiSchemaNameToPseudoJson[documentName];
            const otherUApiSchemaPseudoJson = uApiSchemaNameToPseudoJson[otherDocumentName];
            const def = uApiSchemaPseudoJson[index];
            const otherDef = otherUApiSchemaPseudoJson[otherIndex];
            const errDef = def[defKey];
            const otherErrDef = otherDef[otherDefKey];
            for (let k = 0; k < errDef.length; k++) {
                const thisErrDef = errDef[k];
                const thisErrDefKeys = new Set(Object.keys(thisErrDef));
                thisErrDefKeys.delete('///');
                for (let l = 0; l < otherErrDef.length; l++) {
                    const thisOtherErrDef = otherErrDef[l];
                    const thisOtherErrDefKeys = new Set(Object.keys(thisOtherErrDef));
                    thisOtherErrDefKeys.delete('///');
                    if (thisErrDefKeys.size === thisOtherErrDefKeys.size &&
                        [...thisErrDefKeys].every((key) => thisOtherErrDefKeys.has(key))) {
                        const thisErrorDefKey = thisErrDefKeys.values().next().value;
                        const thisOtherErrorDefKey = thisOtherErrDefKeys.values().next().value;
                        const thisPath = [index, defKey, k, thisErrorDefKey];
                        const thisDocumentJson = documentNamesToJson[documentName];
                        const thisLocation = getPathDocumentCoordinatesPseudoJson(thisPath, thisDocumentJson);
                        parseFailures.push(new SchemaParseFailure(otherDocumentName, [otherIndex, otherDefKey, l, thisOtherErrorDefKey], 'PathCollision', { document: documentName, path: thisPath, location: thisLocation }));
                    }
                }
            }
        }
    }
    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures, documentNamesToJson);
    }
}

function findMatchingSchemaKey(schemaKeys, schemaKey) {
    for (const k of schemaKeys) {
        if (schemaKey.startsWith('info.') && k.startsWith('info.')) {
            return k;
        }
        if (k === schemaKey) {
            return k;
        }
    }
    return null;
}

function findSchemaKey(documentName, definition, index, documentNamesToJson) {
    const regex = /^(((fn|errors|headers|info)|((struct|union|_ext)(<[0-2]>)?))\..*)/;
    const matches = [];
    const keys = Object.keys(definition).sort();
    for (const e of keys) {
        if (regex.test(e)) {
            matches.push(e);
        }
    }
    if (matches.length === 1) {
        return matches[0];
    }
    else {
        const parseFailure = new SchemaParseFailure(documentName, [index], 'ObjectKeyRegexMatchCountUnexpected', {
            regex: regex.toString().slice(1, -1),
            actual: matches.length,
            expected: 1,
            keys: keys,
        });
        throw new UApiSchemaParseError([parseFailure], documentNamesToJson);
    }
}

function validateBoolean(value) {
    if (typeof value === 'boolean') {
        return [];
    }
    else {
        return getTypeUnexpectedValidationFailure([], value, booleanName);
    }
}

function generateRandomBoolean(blueprintValue, useBlueprintValue, ctx) {
    if (useBlueprintValue) {
        return blueprintValue;
    }
    else {
        return ctx.randomGenerator.nextBoolean();
    }
}

const booleanName = 'Boolean';
class UBoolean extends UType {
    getTypeParameterCount() {
        return 0;
    }
    validate(value, typeParameters, ctx) {
        return validateBoolean(value);
    }
    generateRandomValue(blueprintValue, useBlueprintValue, typeParameters, ctx) {
        return generateRandomBoolean(blueprintValue, useBlueprintValue, ctx);
    }
    getName() {
        return booleanName;
    }
}

function validateInteger(value) {
    if (typeof value === 'number' && Number.isInteger(value)) {
        if (value === 9223372036854776000 || value === -9223372036854776e3) {
            return [
                new ValidationFailure([], 'NumberOutOfRange', {}),
                new ValidationFailure([], 'NumberTruncated', {}),
            ];
        }
        return [];
    }
    else {
        return getTypeUnexpectedValidationFailure([], value, integerName);
    }
}

function generateRandomInteger(blueprintValue, useBlueprintValue, ctx) {
    if (useBlueprintValue) {
        return blueprintValue;
    }
    else {
        return ctx.randomGenerator.nextInt();
    }
}

const integerName = 'Integer';
class UInteger extends UType {
    getTypeParameterCount() {
        return 0;
    }
    validate(value, typeParameters, ctx) {
        return validateInteger(value);
    }
    generateRandomValue(blueprintValue, useBlueprintValue, typeParameters, ctx) {
        return generateRandomInteger(blueprintValue, useBlueprintValue, ctx);
    }
    getName() {
        return integerName;
    }
}

function validateNumber(value) {
    if (typeof value === 'number') {
        if ((Number.isInteger(value) && value === 9223372036854776000) || value === -9223372036854776e3) {
            return [
                new ValidationFailure([], 'NumberOutOfRange', {}),
                new ValidationFailure([], 'NumberTruncated', {}),
            ];
        }
        return [];
    }
    else {
        return getTypeUnexpectedValidationFailure([], value, numberName);
    }
}

function generateRandomNumber(blueprintValue, useBlueprintValue, ctx) {
    if (useBlueprintValue) {
        return blueprintValue;
    }
    else {
        return ctx.randomGenerator.nextDouble();
    }
}

const numberName = 'Number';
class UNumber extends UType {
    getTypeParameterCount() {
        return 0;
    }
    validate(value, typeParameters, ctx) {
        return validateNumber(value);
    }
    generateRandomValue(blueprintValue, useBlueprintValue, typeParameters, ctx) {
        return generateRandomNumber(blueprintValue, useBlueprintValue, ctx);
    }
    getName() {
        return numberName;
    }
}

function validateString(value) {
    if (typeof value === 'string') {
        return [];
    }
    else {
        return getTypeUnexpectedValidationFailure([], value, stringName);
    }
}

function generateRandomString(blueprintValue, useBlueprintValue, ctx) {
    if (useBlueprintValue) {
        return blueprintValue;
    }
    else {
        return ctx.randomGenerator.nextString();
    }
}

const stringName = 'String';
class UString extends UType {
    getTypeParameterCount() {
        return 0;
    }
    validate(value, typeParameters, ctx) {
        return validateString(value);
    }
    generateRandomValue(blueprintValue, useBlueprintValue, typeParameters, ctx) {
        return generateRandomString(blueprintValue, useBlueprintValue, ctx);
    }
    getName() {
        return stringName;
    }
}

function generateRandomAny(ctx) {
    const selectType = ctx.randomGenerator.nextIntWithCeiling(3);
    if (selectType === 0) {
        return ctx.randomGenerator.nextBoolean();
    }
    else if (selectType === 1) {
        return ctx.randomGenerator.nextInt();
    }
    else {
        return ctx.randomGenerator.nextString();
    }
}

const anyName = 'Any';
class UAny extends UType {
    getTypeParameterCount() {
        return 0;
    }
    validate(value, typeParameters, ctx) {
        return [];
    }
    generateRandomValue(blueprintValue, useBlueprintValue, typeParameters, ctx) {
        return generateRandomAny(ctx);
    }
    getName() {
        return anyName;
    }
}

function getTypeUnexpectedParseFailure(documentName, path, value, expectedType) {
    const actualType = getType(value);
    const data = {
        actual: { [actualType]: {} },
        expected: { [expectedType]: {} },
    };
    return [new SchemaParseFailure(documentName, path, 'TypeUnexpected', data)];
}

class UFieldDeclaration {
    fieldName;
    typeDeclaration;
    optional;
    constructor(fieldName, typeDeclaration, optional) {
        this.fieldName = fieldName;
        this.typeDeclaration = typeDeclaration;
        this.optional = optional;
    }
}

function parseTypeDeclaration(path, typeDeclarationArray, ctx) {
    if (!typeDeclarationArray.length) {
        throw new UApiSchemaParseError([new SchemaParseFailure(ctx.documentName, path, 'EmptyArrayDisallowed', {})], ctx.uapiSchemaDocumentNamesToJson);
    }
    const basePath = path.concat([0]);
    const baseType = typeDeclarationArray[0];
    if (typeof baseType !== 'string') {
        const thisParseFailures = getTypeUnexpectedParseFailure(ctx.documentName, basePath, baseType, 'String');
        throw new UApiSchemaParseError(thisParseFailures, ctx.uapiSchemaDocumentNamesToJson);
    }
    const rootTypeString = baseType;
    const regexString = /^(.+?)(\?)?$/;
    const regex = new RegExp(regexString);
    const matcher = rootTypeString.match(regex);
    if (!matcher) {
        throw new UApiSchemaParseError([
            new SchemaParseFailure(ctx.documentName, basePath, 'StringRegexMatchFailed', {
                regex: regexString.toString().slice(1, -1),
            }),
        ], ctx.uapiSchemaDocumentNamesToJson);
    }
    const typeName = matcher[1];
    const nullable = !!matcher[2];
    const type_ = getOrParseType(basePath, typeName, ctx);
    const givenTypeParameterCount = typeDeclarationArray.length - 1;
    if (type_.getTypeParameterCount() !== givenTypeParameterCount) {
        throw new UApiSchemaParseError([
            new SchemaParseFailure(ctx.documentName, path, 'ArrayLengthUnexpected', {
                actual: typeDeclarationArray.length,
                expected: type_.getTypeParameterCount() + 1,
            }),
        ], ctx.uapiSchemaDocumentNamesToJson);
    }
    const parseFailures = [];
    const typeParameters = [];
    const givenTypeParameters = typeDeclarationArray.slice(1);
    for (let index = 1; index <= givenTypeParameters.length; index++) {
        const e = givenTypeParameters[index - 1];
        const loopPath = path.concat([index]);
        if (!Array.isArray(e)) {
            const thisParseFailures = getTypeUnexpectedParseFailure(ctx.documentName, loopPath, e, 'Array');
            parseFailures.push(...thisParseFailures);
            continue;
        }
        try {
            const typeParameterTypeDeclaration = parseTypeDeclaration(loopPath, e, ctx);
            typeParameters.push(typeParameterTypeDeclaration);
        }
        catch (e2) {
            parseFailures.push(...e2.schemaParseFailures);
        }
    }
    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures, ctx.uapiSchemaDocumentNamesToJson);
    }
    return new UTypeDeclaration(type_, nullable, typeParameters);
}

function parseField(path, fieldDeclaration, typeDeclarationValue, ctx) {
    const regexString = '^([a-z][a-zA-Z0-9_]*)(!)?$';
    const regex = new RegExp(regexString);
    const matcher = fieldDeclaration.match(regex);
    if (!matcher) {
        const finalPath = [...path, fieldDeclaration];
        throw new UApiSchemaParseError([new SchemaParseFailure(ctx.documentName, finalPath, 'KeyRegexMatchFailed', { regex: regexString })], ctx.uapiSchemaDocumentNamesToJson);
    }
    const fieldName = matcher[0];
    const optional = Boolean(matcher[2]);
    const thisPath = [...path, fieldName];
    if (!Array.isArray(typeDeclarationValue)) {
        throw new UApiSchemaParseError(getTypeUnexpectedParseFailure(ctx.documentName, thisPath, typeDeclarationValue, 'Array'), ctx.uapiSchemaDocumentNamesToJson);
    }
    const typeDeclarationArray = typeDeclarationValue;
    const typeDeclaration = parseTypeDeclaration(thisPath, typeDeclarationArray, ctx);
    return new UFieldDeclaration(fieldName, typeDeclaration, optional);
}

function parseStructFields(path, referenceStruct, ctx) {
    const parseFailures = [];
    const fields = {};
    for (const fieldDeclaration in referenceStruct) {
        for (const existingField in fields) {
            const existingFieldNoOpt = existingField.split('!')[0];
            const fieldNoOpt = fieldDeclaration.split('!')[0];
            if (fieldNoOpt === existingFieldNoOpt) {
                const finalPath = [...path, fieldDeclaration];
                const finalOtherPath = [...path, existingField];
                const finalOtherDocumentJson = ctx.uapiSchemaDocumentNamesToJson[ctx.documentName];
                const finalOtherLocation = getPathDocumentCoordinatesPseudoJson(finalOtherPath, finalOtherDocumentJson);
                parseFailures.push(new SchemaParseFailure(ctx.documentName, finalPath, 'PathCollision', {
                    document: ctx.documentName,
                    location: finalOtherLocation,
                    path: finalOtherPath,
                }));
            }
        }
        try {
            const parsedField = parseField(path, fieldDeclaration, referenceStruct[fieldDeclaration], ctx);
            const fieldName = parsedField.fieldName;
            fields[fieldName] = parsedField;
        }
        catch (e) {
            if (e instanceof UApiSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            }
            else {
                throw e;
            }
        }
    }
    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures, ctx.uapiSchemaDocumentNamesToJson);
    }
    return fields;
}

function parseStructType(path, structDefinitionAsPseudoJson, schemaKey, ignoreKeys, ctx) {
    const parseFailures = [];
    const otherKeys = new Set(Object.keys(structDefinitionAsPseudoJson));
    otherKeys.delete(schemaKey);
    otherKeys.delete('///');
    otherKeys.delete('_ignoreIfDuplicate');
    for (const ignoreKey of ignoreKeys) {
        otherKeys.delete(ignoreKey);
    }
    if (otherKeys.size > 0) {
        for (const k of otherKeys) {
            const loopPath = [...path, k];
            parseFailures.push(new SchemaParseFailure(ctx.documentName, loopPath, 'ObjectKeyDisallowed', {}));
        }
    }
    const thisPath = [...path, schemaKey];
    const defInit = structDefinitionAsPseudoJson[schemaKey];
    let definition = null;
    if (typeof defInit !== 'object' || Array.isArray(defInit) || defInit === null || defInit === undefined) {
        const branchParseFailures = getTypeUnexpectedParseFailure(ctx.documentName, thisPath, defInit, 'Object');
        parseFailures.push(...branchParseFailures);
    }
    else {
        definition = defInit;
    }
    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures, ctx.uapiSchemaDocumentNamesToJson);
    }
    const fields = parseStructFields(thisPath, definition, ctx);
    return new UStruct(schemaKey, fields);
}

function parseUnionType(path, unionDefinitionAsPseudoJson, schemaKey, ignoreKeys, requiredKeys, ctx) {
    const parseFailures = [];
    const otherKeys = new Set(Object.keys(unionDefinitionAsPseudoJson));
    otherKeys.delete(schemaKey);
    otherKeys.delete("///");
    for (const ignoreKey of ignoreKeys) {
        otherKeys.delete(ignoreKey);
    }
    if (otherKeys.size > 0) {
        for (const k of otherKeys) {
            const loopPath = path.concat(k);
            parseFailures.push(new SchemaParseFailure(ctx.documentName, loopPath, "ObjectKeyDisallowed", {}));
        }
    }
    const thisPath = path.concat(schemaKey);
    const defInit = unionDefinitionAsPseudoJson[schemaKey];
    if (!Array.isArray(defInit)) {
        const finalParseFailures = getTypeUnexpectedParseFailure(ctx.documentName, thisPath, defInit, "Array");
        parseFailures.push(...finalParseFailures);
        throw new UApiSchemaParseError(parseFailures, ctx.uapiSchemaDocumentNamesToJson);
    }
    const definition2 = defInit;
    const definition = [];
    let index = -1;
    for (const element of definition2) {
        index += 1;
        const loopPath = thisPath.concat(index);
        if (typeof element !== "object" || Array.isArray(element) || element === null || element === undefined) {
            const thisParseFailures = getTypeUnexpectedParseFailure(ctx.documentName, loopPath, element, "Object");
            parseFailures.push(...thisParseFailures);
            continue;
        }
        definition.push(element);
    }
    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures, ctx.uapiSchemaDocumentNamesToJson);
    }
    if (definition.length === 0) {
        parseFailures.push(new SchemaParseFailure(ctx.documentName, thisPath, "EmptyArrayDisallowed", {}));
    }
    else {
        for (const requiredKey of requiredKeys) {
            let found = false;
            for (const element of definition) {
                const tagKeys = new Set(Object.keys(element));
                tagKeys.delete("///");
                if (tagKeys.has(requiredKey)) {
                    found = true;
                    break;
                }
            }
            if (!found) {
                parseFailures.push(new SchemaParseFailure(ctx.documentName, thisPath, "RequiredObjectKeyMissing", {
                    key: requiredKey,
                }));
            }
        }
    }
    const tags = {};
    const tagIndices = {};
    for (let i = 0; i < definition.length; i++) {
        const element = definition[i];
        const loopPath = thisPath.concat(i);
        const mapInit = element;
        const map = Object.fromEntries(Object.entries(mapInit));
        delete map["///"];
        const keys = Object.keys(map);
        const regexString = "^([A-Z][a-zA-Z0-9_]*)$";
        const regex = new RegExp(regexString);
        const matches = keys.filter((k) => regex.test(k));
        if (matches.length !== 1) {
            parseFailures.push(new SchemaParseFailure(ctx.documentName, loopPath, "ObjectKeyRegexMatchCountUnexpected", {
                regex: regexString,
                actual: matches.length,
                expected: 1,
                keys: keys,
            }));
            continue;
        }
        if (Object.keys(map).length !== 1) {
            parseFailures.push(new SchemaParseFailure(ctx.documentName, loopPath, "ObjectSizeUnexpected", {
                expected: 1,
                actual: Object.keys(map).length,
            }));
            continue;
        }
        const entry = Object.entries(map)[0];
        const unionTag = entry[0];
        const unionKeyPath = loopPath.concat(unionTag);
        if (typeof entry[1] !== "object" || Array.isArray(entry[1]) || entry[1] === null || entry[1] === undefined) {
            const thisParseFailures = getTypeUnexpectedParseFailure(ctx.documentName, unionKeyPath, entry[1], "Object");
            parseFailures.push(...thisParseFailures);
            continue;
        }
        const unionTagStruct = entry[1];
        try {
            const fields = parseStructFields(unionKeyPath, unionTagStruct, ctx);
            const unionStruct = new UStruct(`${schemaKey}.${unionTag}`, fields);
            tags[unionTag] = unionStruct;
            tagIndices[unionTag] = i;
        }
        catch (e) {
            if (e instanceof UApiSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            }
            else {
                throw e;
            }
        }
    }
    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures, ctx.uapiSchemaDocumentNamesToJson);
    }
    return new UUnion(schemaKey, tags, tagIndices);
}

function derivePossibleSelect(fnName, result) {
    const nestedTypes = {};
    const okFields = result.tags["Ok_"].fields;
    const okFieldNames = Object.keys(okFields);
    okFieldNames.sort();
    findNestedTypes(okFields, nestedTypes);
    const possibleSelect = {};
    possibleSelect["->"] = {
        Ok_: okFieldNames,
    };
    const sortedTypeKeys = Object.keys(nestedTypes).sort();
    for (const k of sortedTypeKeys) {
        console.log(`k: ${k}`);
        const v = nestedTypes[k];
        if (v instanceof UUnion) {
            const unionSelect = {};
            const sortedTagKeys = Object.keys(v.tags).sort();
            for (const c of sortedTagKeys) {
                const typ = v.tags[c];
                const selectedFieldNames = [];
                const sortedFieldNames = Object.keys(typ.fields).sort();
                for (const fieldName of sortedFieldNames) {
                    selectedFieldNames.push(fieldName);
                }
                unionSelect[c] = selectedFieldNames;
            }
            possibleSelect[k] = unionSelect;
        }
        else if (v instanceof UStruct) {
            const structSelect = [];
            const sortedFieldNames = Object.keys(v.fields).sort();
            for (const fieldName of sortedFieldNames) {
                structSelect.push(fieldName);
            }
            possibleSelect[k] = structSelect;
        }
    }
    return possibleSelect;
}
function findNestedTypes(fields, nestedTypes) {
    for (const field of Object.values(fields)) {
        const typ = field.typeDeclaration.type;
        if (typ instanceof UUnion) {
            nestedTypes[typ.name] = typ;
            for (const c of Object.values(typ.tags)) {
                findNestedTypes(c.fields, nestedTypes);
            }
        }
        else if (typ instanceof UStruct) {
            nestedTypes[typ.name] = typ;
            findNestedTypes(typ.fields, nestedTypes);
        }
    }
}

function parseFunctionType(path, functionDefinitionAsParsedJson, schemaKey, ctx) {
    const parseFailures = [];
    let callType = null;
    try {
        const argType = parseStructType(path, functionDefinitionAsParsedJson, schemaKey, ['->', '_errors'], ctx);
        callType = new UUnion(schemaKey, { [schemaKey]: argType }, { [schemaKey]: 0 });
    }
    catch (e) {
        if (e instanceof UApiSchemaParseError) {
            parseFailures.push(...e.schemaParseFailures);
        }
        else {
            throw e;
        }
    }
    const resultSchemaKey = '->';
    let resultType = null;
    if (!(resultSchemaKey in functionDefinitionAsParsedJson)) {
        parseFailures.push(new SchemaParseFailure(ctx.documentName, path, 'RequiredObjectKeyMissing', { key: resultSchemaKey }));
    }
    else {
        try {
            resultType = parseUnionType(path, functionDefinitionAsParsedJson, resultSchemaKey, Object.keys(functionDefinitionAsParsedJson), ['Ok_'], ctx);
        }
        catch (e) {
            if (e instanceof UApiSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            }
            else {
                throw e;
            }
        }
    }
    const errorsRegexKey = '_errors';
    const regexPath = [...path, errorsRegexKey];
    let errorsRegex = null;
    if (errorsRegexKey in functionDefinitionAsParsedJson && !schemaKey.endsWith('_')) {
        parseFailures.push(new SchemaParseFailure(ctx.documentName, regexPath, 'ObjectKeyDisallowed', {}));
    }
    else {
        const errorsRegexInit = errorsRegexKey in functionDefinitionAsParsedJson
            ? functionDefinitionAsParsedJson[errorsRegexKey]
            : '^errors\\..*$';
        if (typeof errorsRegexInit !== 'string') {
            const thisParseFailures = getTypeUnexpectedParseFailure(ctx.documentName, regexPath, errorsRegexInit, 'String');
            parseFailures.push(...thisParseFailures);
        }
        else {
            errorsRegex = errorsRegexInit;
        }
    }
    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures, ctx.uapiSchemaDocumentNamesToJson);
    }
    const fnSelectType = derivePossibleSelect(schemaKey, resultType);
    const selectType = getOrParseType([], '_ext.Select_', ctx);
    selectType.possibleSelects[schemaKey] = fnSelectType;
    return new UFn(schemaKey, callType, resultType, errorsRegex);
}

function validateSelect(givenObj, possibleFnSelects, ctx) {
    if (typeof givenObj !== 'object' || Array.isArray(givenObj) || givenObj === null || givenObj === undefined) {
        return getTypeUnexpectedValidationFailure([], givenObj, 'Object');
    }
    const possibleSelect = possibleFnSelects[ctx.fn];
    return isSubSelect([], givenObj, possibleSelect);
}
function isSubSelect(path, givenObj, possibleSelectSection) {
    console.log(`validating ${path.join('.')} with givenObject: ${JSON.stringify(givenObj)} and possibleSelectSection: ${JSON.stringify(possibleSelectSection)}`);
    if (Array.isArray(possibleSelectSection)) {
        if (!Array.isArray(givenObj)) {
            return getTypeUnexpectedValidationFailure(path, givenObj, 'Array');
        }
        const validationFailures = [];
        for (const [index, element] of givenObj.entries()) {
            if (!possibleSelectSection.includes(element)) {
                validationFailures.push(new ValidationFailure([...path, index], 'ArrayElementDisallowed', {}));
            }
        }
        return validationFailures;
    }
    else if (typeof possibleSelectSection === 'object' && !Array.isArray(possibleSelectSection)) {
        if (typeof givenObj !== 'object' || Array.isArray(givenObj) || givenObj === null) {
            return getTypeUnexpectedValidationFailure(path, givenObj, 'Object');
        }
        const validationFailures = [];
        for (const [key, value] of Object.entries(givenObj)) {
            if (key in possibleSelectSection) {
                const innerFailures = isSubSelect([...path, key], value, possibleSelectSection[key]);
                validationFailures.push(...innerFailures);
            }
            else {
                validationFailures.push(new ValidationFailure([...path, key], 'ObjectKeyDisallowed', {}));
            }
        }
        return validationFailures;
    }
    return [];
}

function generateRandomSelect(possibleSelects, ctx) {
    const possibleSelect = possibleSelects[ctx.fnScope];
    return subSelect(possibleSelect, ctx);
}
function subSelect(possibleSelectSection, ctx) {
    if (Array.isArray(possibleSelectSection)) {
        const selectedFieldNames = [];
        for (const fieldName of possibleSelectSection) {
            if (ctx.randomGenerator.nextBoolean()) {
                selectedFieldNames.push(fieldName);
            }
        }
        return selectedFieldNames;
    }
    else if (typeof possibleSelectSection === 'object' && !Array.isArray(possibleSelectSection)) {
        const selectedSection = {};
        for (const [key, value] of Object.entries(possibleSelectSection)) {
            if (ctx.randomGenerator.nextBoolean()) {
                const result = subSelect(value, ctx);
                if (typeof result === 'object' && !Array.isArray(result) && Object.keys(result).length === 0) {
                    continue;
                }
                selectedSection[key] = result;
            }
        }
        return selectedSection;
    }
    else {
        throw new Error('Invalid possibleSelectSection');
    }
}

const select = 'Object';
class USelect {
    possibleSelects = {};
    getTypeParameterCount() {
        return 0;
    }
    validate(givenObj, typeParameters, ctx) {
        return validateSelect(givenObj, this.possibleSelects, ctx);
    }
    generateRandomValue(blueprintValue, useBlueprintValue, typeParameters, ctx) {
        return generateRandomSelect(this.possibleSelects, ctx);
    }
    getName() {
        return select;
    }
}

function validateMockCall(givenObj, types, ctx) {
    if (!(typeof givenObj === "object" && !Array.isArray(givenObj))) {
        return getTypeUnexpectedValidationFailure([], givenObj, "Object");
    }
    const givenMap = givenObj;
    const regexString = /^fn\..*$/;
    const keys = Object.keys(givenMap).sort();
    const matches = keys.filter((k) => regexString.test(k));
    if (matches.length !== 1) {
        return [
            new ValidationFailure([], "ObjectKeyRegexMatchCountUnexpected", {
                regex: regexString.toString().slice(1, -1),
                actual: matches.length,
                expected: 1,
                keys,
            }),
        ];
    }
    const functionName = matches[0];
    const functionDef = types[functionName];
    const input = givenMap[functionName];
    const functionDefCall = functionDef.call;
    const functionDefName = functionDef.name;
    const functionDefCallTags = functionDefCall.tags;
    const inputFailures = functionDefCallTags[functionDefName].validate(input, [], ctx);
    const inputFailuresWithPath = [];
    for (const failure of inputFailures) {
        const newPath = [functionName, ...failure.path];
        inputFailuresWithPath.push(new ValidationFailure(newPath, failure.reason, failure.data));
    }
    return inputFailuresWithPath.filter((failure) => failure.reason !== "RequiredObjectKeyMissing");
}

function generateRandomUMockCall(types, ctx) {
    const functions = Object.entries(types)
        .filter(([key, value]) => value instanceof UFn)
        .filter(([key, value]) => !key.endsWith("_"))
        .map(([key, value]) => value);
    functions.sort((fn1, fn2) => fn1.name.localeCompare(fn2.name));
    const selectedFn = functions[Math.floor(ctx.randomGenerator.nextIntWithCeiling(functions.length))];
    return generateRandomUnion(null, false, selectedFn.call.tags, ctx.copy({ alwaysIncludeRequiredFields: false }));
}

const mockCallName = '_ext.Call_';
class UMockCall extends UType {
    types;
    constructor(types) {
        super();
        this.types = types;
    }
    getTypeParameterCount() {
        return 0;
    }
    validate(givenObj, typeParameters, ctx) {
        return validateMockCall(givenObj, this.types, ctx);
    }
    generateRandomValue(blueprintValue, useBlueprintValue, typeParameters, ctx) {
        return generateRandomUMockCall(this.types, ctx);
    }
    getName() {
        return mockCallName;
    }
}

function validateMockStub(givenObj, types, ctx) {
    const validationFailures = [];
    if (!(typeof givenObj === "object" && !Array.isArray(givenObj))) {
        return getTypeUnexpectedValidationFailure([], givenObj, "Object");
    }
    const givenMap = givenObj;
    const regexString = /^fn\..*$/;
    const keys = Object.keys(givenMap).sort();
    const matches = keys.filter((k) => regexString.test(k));
    if (matches.length !== 1) {
        return [
            new ValidationFailure([], "ObjectKeyRegexMatchCountUnexpected", {
                regex: regexString.toString().slice(1, -1),
                actual: matches.length,
                expected: 1,
                keys: keys,
            }),
        ];
    }
    const functionName = matches[0];
    const functionDef = types[functionName];
    const input = givenMap[functionName];
    const functionDefCall = functionDef.call;
    const functionDefName = functionDef.name;
    const functionDefCallTags = functionDefCall.tags;
    const inputFailures = functionDefCallTags[functionDefName].validate(input, [], ctx);
    const inputFailuresWithPath = [];
    for (const f of inputFailures) {
        const thisPath = [functionName, ...f.path];
        inputFailuresWithPath.push(new ValidationFailure(thisPath, f.reason, f.data));
    }
    const inputFailuresWithoutMissingRequired = inputFailuresWithPath.filter((f) => f.reason !== "RequiredObjectKeyMissing");
    validationFailures.push(...inputFailuresWithoutMissingRequired);
    const resultDefKey = "->";
    if (!(resultDefKey in givenMap)) {
        validationFailures.push(new ValidationFailure([], "RequiredObjectKeyMissing", { key: resultDefKey }));
    }
    else {
        const output = givenMap[resultDefKey];
        const outputFailures = functionDef.result.validate(output, [], ctx);
        const outputFailuresWithPath = [];
        for (const f of outputFailures) {
            const thisPath = [resultDefKey, ...f.path];
            outputFailuresWithPath.push(new ValidationFailure(thisPath, f.reason, f.data));
        }
        const failuresWithoutMissingRequired = outputFailuresWithPath.filter((f) => f.reason !== "RequiredObjectKeyMissing");
        validationFailures.push(...failuresWithoutMissingRequired);
    }
    const disallowedFields = Object.keys(givenMap).filter((k) => !matches.includes(k) && k !== resultDefKey);
    for (const disallowedField of disallowedFields) {
        validationFailures.push(new ValidationFailure([disallowedField], "ObjectKeyDisallowed", {}));
    }
    return validationFailures;
}

function generateRandomUMockStub(types, ctx) {
    const functions = Object.entries(types)
        .filter(([key, value]) => value instanceof UFn)
        .filter(([key, value]) => !key.endsWith("_"))
        .map(([key, value]) => value);
    functions.sort((fn1, fn2) => fn1.name.localeCompare(fn2.name));
    console.log(`randomSeed: ${ctx.randomGenerator.seed}`);
    console.log(`functions: ${JSON.stringify(functions.map((fn) => fn.name))}`);
    const index = ctx.randomGenerator.nextIntWithCeiling(functions.length);
    console.log(`index: ${index}`);
    const selectedFn = functions[index];
    console.log(`selectedFn: ${selectedFn.name}`);
    const argFields = selectedFn.call.tags[selectedFn.name].fields;
    const okFields = selectedFn.result.tags["Ok_"].fields;
    const arg = generateRandomStruct(null, false, argFields, ctx.copy({ alwaysIncludeRequiredFields: false }));
    const okResult = generateRandomStruct(null, false, okFields, ctx.copy({ alwaysIncludeRequiredFields: false }));
    return {
        [selectedFn.name]: arg,
        "->": {
            Ok_: okResult,
        },
    };
}

const mockStubName = '_ext.Stub_';
class UMockStub extends UType {
    types;
    constructor(types) {
        super();
        this.types = types;
    }
    getTypeParameterCount() {
        return 0;
    }
    validate(givenObj, typeParameters, ctx) {
        return validateMockStub(givenObj, this.types, ctx);
    }
    generateRandomValue(blueprintValue, useBlueprintValue, typeParameters, ctx) {
        return generateRandomUMockStub(this.types, ctx);
    }
    getName() {
        return mockStubName;
    }
}

function getOrParseType(path, typeName, ctx) {
    if (ctx.failedTypes.has(typeName)) {
        throw new UApiSchemaParseError([], ctx.uapiSchemaDocumentNamesToJson);
    }
    const existingType = ctx.parsedTypes[typeName];
    if (existingType !== undefined) {
        return existingType;
    }
    const regexString = `^(boolean|integer|number|string|any|array|object)|((fn|(union|struct|_ext))\\.([a-zA-Z_]\\w*))$`;
    const regex = new RegExp(regexString);
    const matcher = typeName.match(regex);
    if (!matcher) {
        throw new UApiSchemaParseError([new SchemaParseFailure(ctx.documentName, path, 'StringRegexMatchFailed', { regex: regexString })], ctx.uapiSchemaDocumentNamesToJson);
    }
    const standardTypeName = matcher[1];
    if (standardTypeName) {
        return ({
            boolean: new UBoolean(),
            integer: new UInteger(),
            number: new UNumber(),
            string: new UString(),
            array: new UArray(),
            object: new UObject(),
        }[standardTypeName] || new UAny());
    }
    const customTypeName = matcher[2];
    const thisIndex = ctx.schemaKeysToIndex[customTypeName];
    const thisDocumentName = ctx.schemaKeysToDocumentName[customTypeName];
    if (thisIndex === undefined) {
        throw new UApiSchemaParseError([new SchemaParseFailure(ctx.documentName, path, 'TypeUnknown', { name: customTypeName })], ctx.uapiSchemaDocumentNamesToJson);
    }
    const definition = ctx.uapiSchemaDocumentNamesToPseudoJson[thisDocumentName][thisIndex];
    let type;
    try {
        if (customTypeName.startsWith('struct')) {
            type = parseStructType([thisIndex], definition, customTypeName, [], ctx.copy({ documentName: thisDocumentName }));
        }
        else if (customTypeName.startsWith('union')) {
            type = parseUnionType([thisIndex], definition, customTypeName, [], [], ctx.copy({ documentName: thisDocumentName }));
        }
        else if (customTypeName.startsWith('fn')) {
            type = parseFunctionType([thisIndex], definition, customTypeName, ctx.copy({ documentName: thisDocumentName }));
        }
        else {
            const possibleTypeExtension = {
                '_ext.Select_': new USelect(),
                '_ext.Call_': new UMockCall(ctx.parsedTypes),
                '_ext.Stub_': new UMockStub(ctx.parsedTypes),
            }[customTypeName];
            if (!possibleTypeExtension) {
                throw new UApiSchemaParseError([
                    new SchemaParseFailure(ctx.documentName, [thisIndex], 'TypeExtensionImplementationMissing', {
                        name: customTypeName,
                    }),
                ], ctx.uapiSchemaDocumentNamesToJson);
            }
            type = possibleTypeExtension;
        }
        ctx.parsedTypes[customTypeName] = type;
        return type;
    }
    catch (e) {
        if (e instanceof UApiSchemaParseError) {
            ctx.allParseFailures.push(...e.schemaParseFailures);
            ctx.failedTypes.add(customTypeName);
            throw new UApiSchemaParseError([], ctx.uapiSchemaDocumentNamesToJson);
        }
        throw e;
    }
}

class UError {
    name;
    errors;
    constructor(name, errors) {
        this.name = name;
        this.errors = errors;
    }
}

function parseErrorType(path, errorDefinitionAsParsedJson, schemaKey, ctx) {
    const parseFailures = [];
    const otherKeys = Object.keys(errorDefinitionAsParsedJson).filter((key) => key !== schemaKey && key !== '///');
    if (otherKeys.length > 0) {
        for (const k of otherKeys) {
            const loopPath = path.concat(k);
            parseFailures.push(new SchemaParseFailure(ctx.documentName, loopPath, 'ObjectKeyDisallowed', {}));
        }
    }
    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures, ctx.uapiSchemaDocumentNamesToJson);
    }
    const error = parseUnionType(path, errorDefinitionAsParsedJson, schemaKey, [], [], ctx);
    return new UError(schemaKey, error);
}

class UHeaders {
    name;
    requestHeaders;
    responseHeaders;
    constructor(name, requestHeaders, responseHeaders) {
        this.name = name;
        this.requestHeaders = requestHeaders;
        this.responseHeaders = responseHeaders;
    }
}

function parseHeadersType(path, headersDefinitionAsParsedJson, schemaKey, ctx) {
    const parseFailures = [];
    const requestHeaders = {};
    const responseHeaders = {};
    const requestHeadersDef = headersDefinitionAsParsedJson[schemaKey];
    const thisPath = [...path, schemaKey];
    if (typeof requestHeadersDef !== 'object' ||
        Array.isArray(requestHeadersDef) ||
        requestHeadersDef === null ||
        requestHeadersDef === undefined) {
        const branchParseFailures = getTypeUnexpectedParseFailure(ctx.documentName, thisPath, requestHeadersDef, 'Object');
        parseFailures.push(...branchParseFailures);
    }
    else {
        try {
            const requestFields = parseStructFields(thisPath, requestHeadersDef, ctx);
            // All headers are optional
            for (const field in requestFields) {
                requestFields[field].optional = true;
            }
            Object.assign(requestHeaders, requestFields);
        }
        catch (e) {
            if (e instanceof UApiSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            }
            else {
                throw e;
            }
        }
    }
    const responseKey = '->';
    const responsePath = [...path, responseKey];
    if (!(responseKey in headersDefinitionAsParsedJson)) {
        parseFailures.push(new SchemaParseFailure(ctx.documentName, responsePath, 'RequiredObjectKeyMissing', {
            key: responseKey,
        }));
    }
    const responseHeadersDef = headersDefinitionAsParsedJson[responseKey];
    if (typeof responseHeadersDef !== 'object' ||
        Array.isArray(responseHeadersDef) ||
        responseHeadersDef === null ||
        responseHeadersDef === undefined) {
        const branchParseFailures = getTypeUnexpectedParseFailure(ctx.documentName, thisPath, responseHeadersDef, 'Object');
        parseFailures.push(...branchParseFailures);
    }
    else {
        try {
            const responseFields = parseStructFields(responsePath, responseHeadersDef, ctx);
            // All headers are optional
            for (const field in responseFields) {
                responseFields[field].optional = true;
            }
            Object.assign(responseHeaders, responseFields);
        }
        catch (e) {
            if (e instanceof UApiSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            }
            else {
                throw e;
            }
        }
    }
    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures, ctx.uapiSchemaDocumentNamesToJson);
    }
    return new UHeaders(schemaKey, requestHeaders, responseHeaders);
}

class ParseContext {
    documentName;
    uapiSchemaDocumentNamesToPseudoJson;
    uapiSchemaDocumentNamesToJson;
    schemaKeysToDocumentName;
    schemaKeysToIndex;
    parsedTypes;
    allParseFailures;
    failedTypes;
    constructor(documentName, uapiSchemaDocumentNamesToPseudoJson, uapiSchemaDocumentNamesToJson, schemaKeysToDocumentName, schemaKeysToIndex, parsedTypes, allParseFailures, failedTypes) {
        this.documentName = documentName;
        this.uapiSchemaDocumentNamesToPseudoJson = uapiSchemaDocumentNamesToPseudoJson;
        this.uapiSchemaDocumentNamesToJson = uapiSchemaDocumentNamesToJson;
        this.schemaKeysToDocumentName = schemaKeysToDocumentName;
        this.schemaKeysToIndex = schemaKeysToIndex;
        this.parsedTypes = parsedTypes;
        this.allParseFailures = allParseFailures;
        this.failedTypes = failedTypes;
    }
    copy({ documentName }) {
        return new ParseContext(documentName ?? this.documentName, this.uapiSchemaDocumentNamesToPseudoJson, this.uapiSchemaDocumentNamesToJson, this.schemaKeysToDocumentName, this.schemaKeysToIndex, this.parsedTypes, this.allParseFailures, this.failedTypes);
    }
}

function catchHeaderCollisions(uApiSchemaNameToPseudoJson, headerKeys, keysToIndex, schemaKeysToDocumentNames, documentNamesToJson) {
    const parseFailures = [];
    const headerKeysList = [...headerKeys];
    headerKeysList.sort((k1, k2) => {
        const documentName1 = schemaKeysToDocumentNames[k1];
        const documentName2 = schemaKeysToDocumentNames[k2];
        if (documentName1 !== documentName2) {
            return documentName1.localeCompare(documentName2);
        }
        else {
            const index1 = keysToIndex[k1];
            const index2 = keysToIndex[k2];
            return index1 - index2;
        }
    });
    for (let i = 0; i < headerKeysList.length; i++) {
        for (let j = i + 1; j < headerKeysList.length; j++) {
            const defKey = headerKeysList[i];
            const otherDefKey = headerKeysList[j];
            const index = keysToIndex[defKey];
            const otherIndex = keysToIndex[otherDefKey];
            const documentName = schemaKeysToDocumentNames[defKey];
            const otherDocumentName = schemaKeysToDocumentNames[otherDefKey];
            const uApiSchemaPseudoJson = uApiSchemaNameToPseudoJson[documentName];
            const otherUApiSchemaPseudoJson = uApiSchemaNameToPseudoJson[otherDocumentName];
            const def = uApiSchemaPseudoJson[index];
            const otherDef = otherUApiSchemaPseudoJson[otherIndex];
            const headerDef = def[defKey];
            const otherHeaderDef = otherDef[otherDefKey];
            const headerCollisions = Object.keys(headerDef).filter((k) => k in otherHeaderDef);
            for (const headerCollision of headerCollisions) {
                const thisPath = [index, defKey, headerCollision];
                const thisDocumentJson = documentNamesToJson[documentName];
                const thisLocation = getPathDocumentCoordinatesPseudoJson(thisPath, thisDocumentJson);
                parseFailures.push(new SchemaParseFailure(otherDocumentName, [otherIndex, otherDefKey, headerCollision], 'PathCollision', { document: documentName, path: thisPath, location: thisLocation }));
            }
            const resHeaderDef = def['->'];
            const otherResHeaderDef = otherDef['->'];
            const resHeaderCollisions = Object.keys(resHeaderDef).filter((k) => k in otherResHeaderDef);
            for (const resHeaderCollision of resHeaderCollisions) {
                const thisPath = [index, '->', resHeaderCollision];
                const thisDocumentJson = documentNamesToJson[documentName];
                const thisLocation = getPathDocumentCoordinatesPseudoJson(thisPath, thisDocumentJson);
                parseFailures.push(new SchemaParseFailure(otherDocumentName, [otherIndex, '->', resHeaderCollision], 'PathCollision', {
                    document: documentName,
                    path: thisPath,
                    location: thisLocation,
                }));
            }
        }
    }
    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures, documentNamesToJson);
    }
}

function parseUApiSchema(uApiSchemaDocumentNamesToJson) {
    const originalSchema = {};
    const fullSchema = {};
    const parsedTypes = {};
    const parseFailures = [];
    const failedTypes = new Set();
    const schemaKeysToIndex = {};
    const schemaKeysToDocumentName = {};
    const schemaKeys = new Set();
    const orderedDocumentNames = Object.keys(uApiSchemaDocumentNamesToJson).sort();
    const uApiSchemaDocumentNamesToPseudoJson = {};
    for (const [documentName, jsonValue] of Object.entries(uApiSchemaDocumentNamesToJson)) {
        let uApiSchemaPseudoJsonInit;
        try {
            uApiSchemaPseudoJsonInit = JSON.parse(jsonValue);
        }
        catch (e) {
            throw new UApiSchemaParseError([new SchemaParseFailure(documentName, [], 'JsonInvalid', {})], uApiSchemaDocumentNamesToJson, e);
        }
        if (!Array.isArray(uApiSchemaPseudoJsonInit)) {
            const thisParseFailure = getTypeUnexpectedParseFailure(documentName, [], uApiSchemaPseudoJsonInit, 'Array');
            throw new UApiSchemaParseError(thisParseFailure, uApiSchemaDocumentNamesToJson);
        }
        const uApiSchemaPseudoJson = uApiSchemaPseudoJsonInit;
        uApiSchemaDocumentNamesToPseudoJson[documentName] = uApiSchemaPseudoJson;
    }
    for (const documentName of orderedDocumentNames) {
        const uApiSchemaPseudoJson = uApiSchemaDocumentNamesToPseudoJson[documentName];
        let index = -1;
        for (const definition of uApiSchemaPseudoJson) {
            index += 1;
            const loopPath = [index];
            if (typeof definition !== 'object' ||
                Array.isArray(definition) ||
                definition === null ||
                definition === undefined) {
                const thisParseFailures = getTypeUnexpectedParseFailure(documentName, loopPath, definition, 'Object');
                parseFailures.push(...thisParseFailures);
                continue;
            }
            const def_ = definition;
            try {
                const schemaKey = findSchemaKey(documentName, def_, index, uApiSchemaDocumentNamesToJson);
                const matchingSchemaKey = findMatchingSchemaKey(schemaKeys, schemaKey);
                if (matchingSchemaKey !== null) {
                    const otherPathIndex = schemaKeysToIndex[matchingSchemaKey];
                    const otherDocumentName = schemaKeysToDocumentName[matchingSchemaKey];
                    const finalPath = [...loopPath, schemaKey];
                    const otherFinalPath = [otherPathIndex, matchingSchemaKey];
                    const otherDocumentJson = uApiSchemaDocumentNamesToJson[otherDocumentName];
                    const otherLocationPseudoJson = getPathDocumentCoordinatesPseudoJson(otherFinalPath, otherDocumentJson);
                    parseFailures.push(new SchemaParseFailure(documentName, finalPath, 'PathCollision', {
                        document: otherDocumentName,
                        location: otherLocationPseudoJson,
                        path: [otherPathIndex, matchingSchemaKey],
                    }));
                    continue;
                }
                schemaKeys.add(schemaKey);
                schemaKeysToIndex[schemaKey] = index;
                schemaKeysToDocumentName[schemaKey] = documentName;
                if ('auto_' === documentName || !documentName.endsWith('_')) {
                    originalSchema[schemaKey] = def_;
                }
                fullSchema[schemaKey] = def_;
            }
            catch (e) {
                if (e instanceof UApiSchemaParseError) {
                    parseFailures.push(...e.schemaParseFailures);
                }
                else {
                    throw e;
                }
            }
        }
    }
    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures, uApiSchemaDocumentNamesToJson);
    }
    const headerKeys = new Set();
    const errorKeys = new Set();
    for (const schemaKey of schemaKeys) {
        if (schemaKey.startsWith('info.')) {
            continue;
        }
        else if (schemaKey.startsWith('headers.')) {
            headerKeys.add(schemaKey);
            continue;
        }
        else if (schemaKey.startsWith('errors.')) {
            errorKeys.add(schemaKey);
            continue;
        }
        const thisIndex = schemaKeysToIndex[schemaKey];
        const thisDocumentName = schemaKeysToDocumentName[schemaKey];
        try {
            getOrParseType([thisIndex], schemaKey, new ParseContext(thisDocumentName, uApiSchemaDocumentNamesToPseudoJson, uApiSchemaDocumentNamesToJson, schemaKeysToDocumentName, schemaKeysToIndex, parsedTypes, parseFailures, failedTypes));
        }
        catch (e) {
            if (e instanceof UApiSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            }
            else {
                throw e;
            }
        }
    }
    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures, uApiSchemaDocumentNamesToJson);
    }
    const errors = [];
    try {
        for (const thisKey of errorKeys) {
            const thisIndex = schemaKeysToIndex[thisKey];
            const thisDocumentName = schemaKeysToDocumentName[thisKey];
            const uApiSchemaPseudoJson = uApiSchemaDocumentNamesToPseudoJson[thisDocumentName];
            const def_ = uApiSchemaPseudoJson[thisIndex];
            try {
                const error = parseErrorType([thisIndex], def_, thisKey, new ParseContext(thisDocumentName, uApiSchemaDocumentNamesToPseudoJson, uApiSchemaDocumentNamesToJson, schemaKeysToDocumentName, schemaKeysToIndex, parsedTypes, parseFailures, failedTypes));
                errors.push(error);
            }
            catch (e) {
                if (e instanceof UApiSchemaParseError) {
                    parseFailures.push(...e.schemaParseFailures);
                }
                else {
                    throw e;
                }
            }
        }
    }
    catch (e) {
        if (e instanceof UApiSchemaParseError) {
            parseFailures.push(...e.schemaParseFailures);
        }
        else {
            throw e;
        }
    }
    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures, uApiSchemaDocumentNamesToJson);
    }
    try {
        catchErrorCollisions(uApiSchemaDocumentNamesToPseudoJson, errorKeys, schemaKeysToIndex, schemaKeysToDocumentName, uApiSchemaDocumentNamesToJson);
    }
    catch (e) {
        if (e instanceof UApiSchemaParseError) {
            parseFailures.push(...e.schemaParseFailures);
        }
        else {
            throw e;
        }
    }
    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures, uApiSchemaDocumentNamesToJson);
    }
    for (const error of errors) {
        try {
            applyErrorToParsedTypes(error, parsedTypes, schemaKeysToDocumentName, schemaKeysToIndex, uApiSchemaDocumentNamesToJson);
        }
        catch (e) {
            if (e instanceof UApiSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            }
            else {
                throw e;
            }
        }
    }
    const headers = [];
    for (const headerKey of headerKeys) {
        const thisIndex = schemaKeysToIndex[headerKey];
        const thisDocumentName = schemaKeysToDocumentName[headerKey];
        const uApiSchemaPseudoJson = uApiSchemaDocumentNamesToPseudoJson[thisDocumentName];
        const def_ = uApiSchemaPseudoJson[thisIndex];
        try {
            const headerType = parseHeadersType([thisIndex], def_, headerKey, new ParseContext(thisDocumentName, uApiSchemaDocumentNamesToPseudoJson, uApiSchemaDocumentNamesToJson, schemaKeysToDocumentName, schemaKeysToIndex, parsedTypes, parseFailures, failedTypes));
            headers.push(headerType);
        }
        catch (e) {
            if (e instanceof UApiSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            }
            else {
                throw e;
            }
        }
    }
    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures, uApiSchemaDocumentNamesToJson);
    }
    try {
        catchHeaderCollisions(uApiSchemaDocumentNamesToPseudoJson, headerKeys, schemaKeysToIndex, schemaKeysToDocumentName, uApiSchemaDocumentNamesToJson);
    }
    catch (e) {
        if (e instanceof UApiSchemaParseError) {
            parseFailures.push(...e.schemaParseFailures);
        }
        else {
            throw e;
        }
    }
    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures, uApiSchemaDocumentNamesToJson);
    }
    const requestHeaders = {};
    const responseHeaders = {};
    for (const header of headers) {
        Object.assign(requestHeaders, header.requestHeaders);
        Object.assign(responseHeaders, header.responseHeaders);
    }
    const sortKeys = (a, b) => {
        const aStartsWithInfo = a.startsWith('info.');
        const bStartsWithInfo = b.startsWith('info.');
        if (aStartsWithInfo && !bStartsWithInfo)
            return -1;
        if (!aStartsWithInfo && bStartsWithInfo)
            return 1;
        return a < b ? -1 : a > b ? 1 : 0;
    };
    const sortedSchemaKeys = Object.keys(originalSchema).sort(sortKeys);
    const finalOriginalSchema = sortedSchemaKeys.map((key) => originalSchema[key]);
    const sortedFullSchemaKeys = Object.keys(fullSchema).sort(sortKeys);
    const finalFullSchema = sortedFullSchemaKeys.map((key) => fullSchema[key]);
    return new UApiSchema(finalOriginalSchema, finalFullSchema, parsedTypes, requestHeaders, responseHeaders);
}

function createUApiSchemaFromFileJsonMap(jsonDocuments) {
    const finalJsonDocuments = { ...jsonDocuments };
    finalJsonDocuments["internal_"] = getInternalUApiJson();
    // Determine if we need to add the auth schema
    for (const json of Object.values(jsonDocuments)) {
        const regex = /"struct\.Auth_"\s*:/;
        if (regex.test(json)) {
            finalJsonDocuments["auth_"] = getAuthUApiJson();
            break;
        }
    }
    const uApiSchema = parseUApiSchema(finalJsonDocuments);
    return uApiSchema;
}

function getSchemaFileMap(directory, fs, path) {
    const finalJsonDocuments = {};
    const paths = fs.readdirSync(directory).map((file) => path.join(directory, file));
    for (const filePath of paths) {
        if (filePath.endsWith('.uapi.json')) {
            const content = fs.readFileSync(filePath, 'utf-8');
            const relativePath = path.relative(directory, filePath);
            finalJsonDocuments[relativePath] = content;
        }
    }
    return finalJsonDocuments;
}

class UApiSchema {
    /**
     * A parsed uAPI schema.
     */
    original;
    full;
    parsed;
    parsedRequestHeaders;
    parsedResponseHeaders;
    constructor(original, full, parsed, parsedRequestHeaders, parsedResponseHeaders) {
        this.original = original;
        this.full = full;
        this.parsed = parsed;
        this.parsedRequestHeaders = parsedRequestHeaders;
        this.parsedResponseHeaders = parsedResponseHeaders;
    }
    static fromJson(json) {
        return createUApiSchemaFromFileJsonMap({ auto_: json });
    }
    static fromFileJsonMap(fileJsonMap) {
        return createUApiSchemaFromFileJsonMap(fileJsonMap);
    }
    /**
     * @param fs - node fs
     * @param path - node path
     */
    static fromDirectory(directory, fs, path) {
        // TODO
        const m = getSchemaFileMap(directory, fs, path);
        return createUApiSchemaFromFileJsonMap(m);
    }
}

class MockInvocation {
    functionName;
    functionArgument;
    verified;
    constructor(functionName, functionArgument) {
        this.functionName = functionName;
        this.functionArgument = functionArgument;
        this.verified = false;
    }
}

class MockStub {
    whenFunction;
    whenArgument;
    thenResult;
    allowArgumentPartialMatch;
    count;
    constructor(whenFunction, whenArgument, thenResult, allowArgumentPartialMatch, count) {
        this.whenFunction = whenFunction;
        this.whenArgument = whenArgument;
        this.thenResult = thenResult;
        this.allowArgumentPartialMatch = allowArgumentPartialMatch;
        this.count = count;
    }
}

function partiallyMatches(wholeList, partElement) {
    for (const wholeElement of wholeList) {
        if (isSubMapEntryEqual(partElement, wholeElement)) {
            return true;
        }
    }
    return false;
}

function isSubMapEntryEqual(partValue, wholeValue) {
    if (Array.isArray(partValue) && Array.isArray(wholeValue)) {
        for (let i = 0; i < partValue.length; i += 1) {
            const partElement = partValue[i];
            const partMatches = partiallyMatches(wholeValue, partElement);
            if (!partMatches) {
                return false;
            }
        }
        return true;
    }
    else if (typeof partValue === 'object' && typeof wholeValue === 'object') {
        return isSubMap(partValue, wholeValue);
    }
    else {
        return objectsAreEqual(partValue, wholeValue);
    }
}

function isSubMap(part, whole) {
    for (const partKey in part) {
        const wholeValue = whole[partKey];
        const partValue = part[partKey];
        const entryIsEqual = isSubMapEntryEqual(partValue, wholeValue);
        if (!entryIsEqual) {
            return false;
        }
    }
    return true;
}

function verify(functionName, argument, exactMatch, verificationTimes, invocations) {
    let matchesFound = 0;
    for (const invocation of invocations) {
        if (invocation.functionName === functionName) {
            if (exactMatch) {
                if (objectsAreEqual(invocation.functionArgument, argument)) {
                    invocation.verified = true;
                    matchesFound += 1;
                }
            }
            else {
                const isSubMapResult = isSubMap(argument, invocation.functionArgument);
                if (isSubMapResult) {
                    invocation.verified = true;
                    matchesFound += 1;
                }
            }
        }
    }
    const allCallsPseudoJson = invocations.map((invocation) => ({
        [invocation.functionName]: invocation.functionArgument,
    }));
    const verifyTimesEntry = Object.entries(verificationTimes)[0];
    const verifyKey = verifyTimesEntry[0];
    const verifyTimesStruct = verifyTimesEntry[1];
    let verificationFailurePseudoJson = null;
    if (verifyKey === 'Exact') {
        const times = verifyTimesStruct.times;
        if (matchesFound > times) {
            verificationFailurePseudoJson = {
                TooManyMatchingCalls: {
                    wanted: { Exact: { times } },
                    found: matchesFound,
                    allCalls: allCallsPseudoJson,
                },
            };
        }
        else if (matchesFound < times) {
            verificationFailurePseudoJson = {
                TooFewMatchingCalls: {
                    wanted: { Exact: { times } },
                    found: matchesFound,
                    allCalls: allCallsPseudoJson,
                },
            };
        }
    }
    else if (verifyKey === 'AtMost') {
        const times = verifyTimesStruct.times;
        if (matchesFound > times) {
            verificationFailurePseudoJson = {
                TooManyMatchingCalls: {
                    wanted: { AtMost: { times } },
                    found: matchesFound,
                    allCalls: allCallsPseudoJson,
                },
            };
        }
    }
    else if (verifyKey === 'AtLeast') {
        const times = verifyTimesStruct.times;
        if (matchesFound < times) {
            verificationFailurePseudoJson = {
                TooFewMatchingCalls: {
                    wanted: { AtLeast: { times } },
                    found: matchesFound,
                    allCalls: allCallsPseudoJson,
                },
            };
        }
    }
    if (verificationFailurePseudoJson === null) {
        return { Ok_: {} };
    }
    return { ErrorVerificationFailure: { reason: verificationFailurePseudoJson } };
}

function verifyNoMoreInteractions(invocations) {
    const invocationsNotVerified = invocations.filter((i) => !i.verified);
    if (invocationsNotVerified.length > 0) {
        const unverifiedCallsPseudoJson = invocationsNotVerified.map((invocation) => ({
            [invocation.functionName]: invocation.functionArgument,
        }));
        return {
            ErrorVerificationFailure: {
                additionalUnverifiedCalls: unverifiedCallsPseudoJson,
            },
        };
    }
    return { Ok_: {} };
}

class GenerateContext {
    includeOptionalFields;
    randomizeOptionalFields;
    alwaysIncludeRequiredFields;
    fnScope;
    randomGenerator;
    constructor(includeOptionalFields, randomizeOptionalFields, alwaysIncludeRequiredFields, fnScope, randomGenerator) {
        this.includeOptionalFields = includeOptionalFields;
        this.randomizeOptionalFields = randomizeOptionalFields;
        this.alwaysIncludeRequiredFields = alwaysIncludeRequiredFields;
        this.fnScope = fnScope;
        this.randomGenerator = randomGenerator;
    }
    copy({ alwaysIncludeRequiredFields, }) {
        return new GenerateContext(this.includeOptionalFields, this.randomizeOptionalFields, alwaysIncludeRequiredFields ?? this.alwaysIncludeRequiredFields, this.fnScope, this.randomGenerator);
    }
}

async function mockHandle(requestMessage, stubs, invocations, random, uApiSchema, enableGeneratedDefaultStub, enableOptionalFieldGeneration, randomizeOptionalFieldGeneration) {
    const header = requestMessage.headers;
    const enableGenerationStub = header._gen || false;
    const functionName = requestMessage.getBodyTarget();
    const argument = requestMessage.getBodyPayload();
    if (functionName === 'fn.createStub_') {
        const givenStub = argument.stub;
        const stubCall = Object.entries(givenStub).find(([key]) => key.startsWith('fn.'));
        const [stubFunctionName, stubArg] = stubCall;
        const stubResult = givenStub['->'];
        const allowArgumentPartialMatch = !argument['strictMatch!'] || false;
        const stubCount = argument['count!'] || -1;
        const stub = new MockStub(stubFunctionName, stubArg, stubResult, allowArgumentPartialMatch, stubCount);
        stubs.unshift(stub);
        return new Message({}, { Ok_: {} });
    }
    else if (functionName === 'fn.verify_') {
        const givenCall = argument.call;
        const call = Object.entries(givenCall).find(([key]) => key.startsWith('fn.'));
        const [callFunctionName, callArg] = call;
        const verifyTimes = argument['count!'] || { AtLeast: { times: 1 } };
        const strictMatch = argument['strictMatch!'] || false;
        const verificationResult = verify(callFunctionName, callArg, strictMatch, verifyTimes, invocations);
        return new Message({}, verificationResult);
    }
    else if (functionName === 'fn.verifyNoMoreInteractions_') {
        const verificationResult = verifyNoMoreInteractions(invocations);
        return new Message({}, verificationResult);
    }
    else if (functionName === 'fn.clearCalls_') {
        invocations.length = 0;
        return new Message({}, { Ok_: {} });
    }
    else if (functionName === 'fn.clearStubs_') {
        stubs.length = 0;
        return new Message({}, { Ok_: {} });
    }
    else if (functionName === 'fn.setRandomSeed_') {
        const givenSeed = argument.seed;
        random.setSeed(givenSeed);
        return new Message({}, { Ok_: {} });
    }
    else {
        invocations.push(new MockInvocation(functionName, argument));
        const definition = uApiSchema.parsed[functionName];
        for (const stub of stubs) {
            if (stub.count === 0) {
                continue;
            }
            if (stub.whenFunction === functionName) {
                if (stub.allowArgumentPartialMatch) {
                    if (isSubMap(stub.whenArgument, argument)) {
                        const useBlueprintValue = true;
                        const includeOptionalFields = false;
                        const alwaysIncludeRequiredFields = true;
                        const resultInit = definition.result.generateRandomValue(stub.thenResult, useBlueprintValue, [], new GenerateContext(includeOptionalFields, randomizeOptionalFieldGeneration, alwaysIncludeRequiredFields, functionName, random));
                        const result = resultInit;
                        if (stub.count > 0) {
                            stub.count -= 1;
                        }
                        return new Message({}, result);
                    }
                }
                else {
                    if (objectsAreEqual(stub.whenArgument, argument)) {
                        const useBlueprintValue = true;
                        const includeOptionalFields = false;
                        const alwaysIncludeRequiredFields = true;
                        const resultInit = definition.result.generateRandomValue(stub.thenResult, useBlueprintValue, [], new GenerateContext(includeOptionalFields, randomizeOptionalFieldGeneration, alwaysIncludeRequiredFields, functionName, random));
                        const result = resultInit;
                        if (stub.count > 0) {
                            stub.count -= 1;
                        }
                        return new Message({}, result);
                    }
                }
            }
        }
        if (!enableGeneratedDefaultStub && !enableGenerationStub) {
            return new Message({}, { ErrorNoMatchingStub_: {} });
        }
        if (definition) {
            const resultUnion = definition.result;
            const okStructRef = resultUnion.tags['Ok_'];
            const useBlueprintValue = true;
            const includeOptionalFields = true;
            const alwaysIncludeRequiredFields = true;
            const randomOkStructInit = okStructRef.generateRandomValue({}, useBlueprintValue, [], new GenerateContext(includeOptionalFields, randomizeOptionalFieldGeneration, alwaysIncludeRequiredFields, functionName, random));
            const randomOkStruct = randomOkStructInit;
            return new Message({}, { Ok_: randomOkStruct });
        }
        else {
            throw new UApiError(`Unexpected unknown function: ${functionName}`);
        }
    }
}

class MockServer {
    /**
     * A Mock instance of a uAPI server.
     */
    constructor(mockUApiSchema, options) {
        this.random = new RandomGenerator(options.generatedCollectionLengthMin, options.generatedCollectionLengthMax);
        this.enableGeneratedDefaultStub = options.enableMessageResponseGeneration;
        this.enableOptionalFieldGeneration = options.enableOptionalFieldGeneration;
        this.randomizeOptionalFieldGeneration = options.randomizeOptionalFieldGeneration;
        this.stubs = [];
        this.invocations = [];
        const serverOptions = new ServerOptions();
        serverOptions.onError = options.onError;
        serverOptions.authRequired = false;
        const uApiSchema = new UApiSchema(mockUApiSchema.original, mockUApiSchema.full, mockUApiSchema.parsed, mockUApiSchema.parsedRequestHeaders, mockUApiSchema.parsedResponseHeaders);
        this.server = new Server(uApiSchema, this.handle, serverOptions);
    }
    random;
    enableGeneratedDefaultStub;
    enableOptionalFieldGeneration;
    randomizeOptionalFieldGeneration;
    stubs;
    invocations;
    server;
    async process(message) {
        /**
         * Process a given uAPI Request Message into a uAPI Response Message.
         *
         * @param message - The uAPI request message.
         * @returns The uAPI response message.
         */
        return await this.server.process(message);
    }
    handle = async (requestMessage) => {
        return await mockHandle(requestMessage, this.stubs, this.invocations, this.random, this.server.uApiSchema, this.enableGeneratedDefaultStub, this.enableOptionalFieldGeneration, this.randomizeOptionalFieldGeneration);
    };
}
class MockServerOptions {
    /**
     * Options for the MockServer.
     */
    onError = (e) => { };
    enableMessageResponseGeneration = true;
    enableOptionalFieldGeneration = true;
    randomizeOptionalFieldGeneration = true;
    generatedCollectionLengthMin = 0;
    generatedCollectionLengthMax = 3;
}

class ClientBinaryStrategy {
}

var mockInternalUApi = [
	{
		"///": " A stubbed result for matching input. ",
		"_ext.Stub_": {
		}
	},
	{
		"///": " A call of a function. ",
		"_ext.Call_": {
		}
	},
	{
		"///": " The number of times a function is allowed to be called. ",
		"union.CallCountCriteria_": [
			{
				Exact: {
					times: [
						"integer"
					]
				}
			},
			{
				AtMost: {
					times: [
						"integer"
					]
				}
			},
			{
				AtLeast: {
					times: [
						"integer"
					]
				}
			}
		]
	},
	{
		"///": " Possible causes for a mock verification to fail. ",
		"union.VerificationFailure_": [
			{
				TooFewMatchingCalls: {
					wanted: [
						"union.CallCountCriteria_"
					],
					found: [
						"integer"
					],
					allCalls: [
						"array",
						[
							"_ext.Call_"
						]
					]
				}
			},
			{
				TooManyMatchingCalls: {
					wanted: [
						"union.CallCountCriteria_"
					],
					found: [
						"integer"
					],
					allCalls: [
						"array",
						[
							"_ext.Call_"
						]
					]
				}
			}
		]
	},
	{
		"///": [
			" Create a function stub that will cause the server to return the `stub` result   ",
			" when the `stub` argument matches the function argument on a request.            ",
			"                                                                                 ",
			" If `ignoreMissingArgFields` is `true`, then the server will skip field          ",
			" omission validation on the `stub` argument, and the stub will match calls       ",
			" where the given `stub` argument is Exactly a json sub-structure of the request  ",
			" function argument.                                                              ",
			"                                                                                 ",
			" If `generateMissingResultFields` is `true`, then the server will skip field     ",
			" omission validation on the `stub` result, and the server will generate the      ",
			" necessary data required to make the `result` pass on response validation.       "
		],
		"fn.createStub_": {
			stub: [
				"_ext.Stub_"
			],
			"strictMatch!": [
				"boolean"
			],
			"count!": [
				"integer"
			]
		},
		"->": [
			{
				Ok_: {
				}
			}
		],
		_errors: "^errors\\.Validation_$"
	},
	{
		"///": [
			" Verify a call was made with this mock that matches the given `call` and         ",
			" `multiplicity` criteria. If `allowPartialArgMatch` is supplied as `true`, then  ",
			" the server will skip field omission validation, and match calls where the       ",
			" given `call` argument is Exactly a json sub-structure of the actual argument.   "
		],
		"fn.verify_": {
			call: [
				"_ext.Call_"
			],
			"strictMatch!": [
				"boolean"
			],
			"count!": [
				"union.CallCountCriteria_"
			]
		},
		"->": [
			{
				Ok_: {
				}
			},
			{
				ErrorVerificationFailure: {
					reason: [
						"union.VerificationFailure_"
					]
				}
			}
		],
		_errors: "^errors\\.Validation_$"
	},
	{
		"///": [
			" Verify that no interactions have occurred with this mock or that all            ",
			" interactions have been verified.                                                "
		],
		"fn.verifyNoMoreInteractions_": {
		},
		"->": [
			{
				Ok_: {
				}
			},
			{
				ErrorVerificationFailure: {
					additionalUnverifiedCalls: [
						"array",
						[
							"_ext.Call_"
						]
					]
				}
			}
		],
		_errors: "^errors\\.Validation_$"
	},
	{
		"///": " Clear all stub conditions. ",
		"fn.clearStubs_": {
		},
		"->": [
			{
				Ok_: {
				}
			}
		],
		_errors: "^errors\\.Validation_$"
	},
	{
		"///": " Clear all call data. ",
		"fn.clearCalls_": {
		},
		"->": [
			{
				Ok_: {
				}
			}
		],
		_errors: "^errors\\.Validation_$"
	},
	{
		"///": " Set the seed of the random generator. ",
		"fn.setRandomSeed_": {
			seed: [
				"integer"
			]
		},
		"->": [
			{
				Ok_: {
				}
			}
		],
		_errors: "^errors\\.Validation_$"
	},
	{
		"errors.Mock_": [
			{
				"///": " The mock could not return a result due to no matching stub being available. ",
				ErrorNoMatchingStub_: {
				}
			}
		]
	}
];

function getMockUApiJson() {
    return JSON.stringify(mockInternalUApi);
}

function createMockUApiSchemaFromFileJsonMap(jsonDocuments) {
    const finalJsonDocuments = { ...jsonDocuments };
    finalJsonDocuments['mock_'] = getMockUApiJson();
    const uApiSchema = createUApiSchemaFromFileJsonMap(finalJsonDocuments);
    return new MockUApiSchema(uApiSchema.original, uApiSchema.full, uApiSchema.parsed, uApiSchema.parsedRequestHeaders, uApiSchema.parsedResponseHeaders);
}

class MockUApiSchema {
    /**
     * A parsed uAPI schema.
     */
    original;
    full;
    parsed;
    parsedRequestHeaders;
    parsedResponseHeaders;
    constructor(original, full, parsed, parsedRequestHeaders, parsedResponseHeaders) {
        this.original = original;
        this.full = full;
        this.parsed = parsed;
        this.parsedRequestHeaders = parsedRequestHeaders;
        this.parsedResponseHeaders = parsedResponseHeaders;
    }
    static fromJson(json) {
        return createMockUApiSchemaFromFileJsonMap({ auto_: json });
    }
    static fromFileJsonMap(jsonDocuments) {
        return createMockUApiSchemaFromFileJsonMap(jsonDocuments);
    }
    static fromDirectory(directory, fs, path) {
        const m = getSchemaFileMap(directory, fs, path);
        return createMockUApiSchemaFromFileJsonMap(m);
    }
}

class UApiSchemaFiles {
    filenamesToJson;
    constructor(directory, fs, path) {
        this.filenamesToJson = getSchemaFileMap(directory, fs, path);
    }
}

var $schema = "https://json-schema.org/draft/2020-12/schema";
var type = "array";
var items = {
	oneOf: [
		{
			type: "object",
			additionalProperties: false,
			minProperties: 1,
			patternProperties: {
				"^info\\.[a-zA-Z_]\\w*": {
					type: "object",
					description: "Information about the API.",
					additionalProperties: false
				}
			},
			properties: {
				"///": {
					anyOf: [
						{
							type: "string"
						},
						{
							type: "array",
							items: {
								type: "string"
							}
						}
					]
				}
			}
		},
		{
			type: "object",
			additionalProperties: false,
			minProperties: 1,
			patternProperties: {
				"^struct\\.[a-zA-Z_]\\w*?": {
					type: "object",
					description: "A struct with 0 or more fields.",
					additionalProperties: false,
					patternProperties: {
						"^[a-zA-Z_]\\w*!?$": {
							$ref: "#/$defs/typeDeclaration"
						}
					}
				}
			},
			properties: {
				"///": {
					anyOf: [
						{
							type: "string"
						},
						{
							type: "array",
							items: {
								type: "string"
							}
						}
					]
				}
			}
		},
		{
			type: "object",
			additionalProperties: false,
			minProperties: 1,
			patternProperties: {
				"union\\.[a-zA-Z_]\\w*$": {
					type: "array",
					items: {
						type: "object",
						description: "An union with 1 or more fields huzzah.",
						minProperties: 1,
						patternProperties: {
							"^[a-zA-Z_]\\w*?$": {
								type: "object",
								additionalProperties: false,
								patternProperties: {
									"^[a-zA-Z_]\\w*!?$": {
										$ref: "#/$defs/typeDeclaration"
									}
								}
							}
						},
						"if": {
							properties: {
								"///": {
									type: [
										"string",
										"array"
									]
								}
							}
						},
						then: {
							maxProperties: 2,
							properties: {
								"///": {
									anyOf: [
										{
											type: "string"
										},
										{
											type: "array",
											items: {
												type: "string"
											}
										}
									]
								}
							}
						},
						"else": {
							maxProperties: 1
						}
					}
				}
			},
			properties: {
				"///": {
					anyOf: [
						{
							type: "string"
						},
						{
							type: "array",
							items: {
								type: "string"
							}
						}
					]
				}
			}
		},
		{
			type: "object",
			additionalProperties: false,
			minProperties: 2,
			patternProperties: {
				"^fn\\.[a-zA-Z_]\\w*": {
					description: "A function that accepts an argument struct and returns a result union that is either an `Ok_` struct or an error struct.",
					type: "object",
					additionalProperties: false,
					patternProperties: {
						"^[a-zA-Z_]\\w*!?$": {
							$ref: "#/$defs/typeDeclaration"
						}
					}
				}
			},
			required: [
				"->"
			],
			properties: {
				"->": {
					type: "array",
					prefixItems: [
						{
							type: "object",
							required: [
								"Ok_"
							],
							properties: {
								Ok_: {
									type: "object",
									additionalProperties: false,
									patternProperties: {
										"^[a-zA-Z_]\\w*!?$": {
											$ref: "#/$defs/typeDeclaration"
										}
									}
								}
							},
							additionalProperties: false
						}
					],
					items: {
						type: "object",
						patternProperties: {
							"^[a-zA-Z_]\\w*?$": {
								type: "object",
								additionalProperties: false,
								patternProperties: {
									"^[a-zA-Z_]\\w*!?$": {
										$ref: "#/$defs/typeDeclaration"
									}
								}
							}
						}
					}
				},
				"///": {
					anyOf: [
						{
							type: "string"
						},
						{
							type: "array",
							items: {
								type: "string"
							}
						}
					]
				}
			}
		},
		{
			type: "object",
			additionalProperties: false,
			minProperties: 1,
			patternProperties: {
				"^errors\\.[a-zA-Z_]\\w*": {
					type: "array",
					items: {
						type: "object",
						description: "An union with 1 or more fields huzzah.",
						minProperties: 1,
						patternProperties: {
							"^[a-zA-Z_]\\w*?$": {
								type: "object",
								additionalProperties: false,
								patternProperties: {
									"^[a-zA-Z_]\\w*!?$": {
										$ref: "#/$defs/typeDeclaration"
									}
								}
							}
						},
						"if": {
							properties: {
								"///": {
									type: [
										"string",
										"array"
									]
								}
							}
						},
						then: {
							maxProperties: 2,
							properties: {
								"///": {
									anyOf: [
										{
											type: "string"
										},
										{
											type: "array",
											items: {
												type: "string"
											}
										}
									]
								}
							}
						},
						"else": {
							maxProperties: 1
						}
					}
				}
			},
			properties: {
				"///": {
					anyOf: [
						{
							type: "string"
						},
						{
							type: "array",
							items: {
								type: "string"
							}
						}
					]
				}
			}
		}
	]
};
var $defs = {
	typeDeclaration: {
		type: "array",
		"if": {
			prefixItems: [
				{
					type: "string",
					pattern: "^((boolean|integer|number|string|any)|(fn|union|struct)\\.([a-zA-Z_]\\w*))(\\?)?$"
				}
			]
		},
		then: {
			prefixItems: [
				{
					type: "string",
					pattern: "^((boolean|integer|number|string|any)|(fn|union|struct)\\.([a-zA-Z_]\\w*))(\\?)?$"
				}
			],
			items: false,
			minItems: 1,
			maxItems: 1
		},
		"else": {
			"if": {
				prefixItems: [
					{
						type: "string",
						pattern: "^((array|object)|(fn|(union|struct)<1>)\\.([a-zA-Z_]\\w*))(\\?)?$"
					}
				]
			},
			then: {
				prefixItems: [
					{
						type: "string",
						pattern: "^((array|object)|(fn|(union|struct)<1>)\\.([a-zA-Z_]\\w*))(\\?)?$"
					}
				],
				items: {
					$ref: "#/$defs/typeDeclaration"
				},
				minItems: 2,
				maxItems: 2
			},
			"else": {
				"if": {
					prefixItems: [
						{
							type: "string",
							pattern: "^(fn|(union|struct)<2>)\\.([a-zA-Z_]\\w*)(\\?)?$"
						}
					]
				},
				then: {
					prefixItems: [
						{
							type: "string",
							pattern: "^(fn|(union|struct)<2>)\\.([a-zA-Z_]\\w*)(\\?)?$"
						}
					],
					items: {
						$ref: "#/$defs/typeDeclaration"
					},
					minItems: 3,
					maxItems: 3
				},
				"else": {
					"if": {
						prefixItems: [
							{
								type: "string",
								pattern: "^(fn|(union|struct)<3>)\\.([a-zA-Z_]\\w*)(\\?)?$"
							}
						]
					},
					then: {
						prefixItems: [
							{
								type: "string",
								pattern: "^(fn|(union|struct)<3>)\\.([a-zA-Z_]\\w*)(\\?)?$"
							}
						],
						items: {
							$ref: "#/$defs/typeDeclaration"
						},
						minItems: 4,
						maxItems: 4
					},
					"else": {
						prefixItems: [
							{
								type: "string",
								pattern: "^((boolean|integer|number|string|any|array|object)|(fn|(union|struct)(<[0-3]>)?)\\.([a-zA-Z_]\\w*))(\\?)?$"
							}
						]
					}
				}
			}
		}
	}
};
var jsonSchema = {
	$schema: $schema,
	type: type,
	items: items,
	$defs: $defs
};

const _internal = {
    GenerateContext,
    UFn,
};

exports.Checksum = Checksum;
exports.Client = Client;
exports.ClientBinaryStrategy = ClientBinaryStrategy;
exports.ClientOptions = ClientOptions;
exports.DefaultClientBinaryStrategy = DefaultClientBinaryStrategy;
exports.Message = Message;
exports.MockServer = MockServer;
exports.MockServerOptions = MockServerOptions;
exports.MockUApiSchema = MockUApiSchema;
exports.RandomGenerator = RandomGenerator;
exports.SerializationError = SerializationError;
exports.Serializer = Serializer;
exports.Server = Server;
exports.ServerOptions = ServerOptions;
exports.UApiSchema = UApiSchema;
exports.UApiSchemaFiles = UApiSchemaFiles;
exports.UApiSchemaParseError = UApiSchemaParseError;
exports._internal = _internal;
exports.jsonSchema = jsonSchema;
//# sourceMappingURL=index.cjs.js.map
