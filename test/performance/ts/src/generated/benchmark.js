//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

/*eslint-disable block-scoped-var, id-length, no-control-regex, no-magic-numbers, no-prototype-builtins, no-redeclare, no-shadow, no-var, sort-vars, default-case, jsdoc/require-param*/
import $protobuf from "protobufjs/minimal.js";

// Common aliases
const $Reader = $protobuf.Reader, $Writer = $protobuf.Writer, $util = $protobuf.util;

// Exported root namespace
const $root = $protobuf.roots["default"] || ($protobuf.roots["default"] = {});

export const telepact = $root.telepact = (() => {

    /**
     * Namespace telepact.
     * @exports telepact
     * @namespace
     */
    const telepact = {};

    telepact.performance = (function() {

        /**
         * Namespace performance.
         * @memberof telepact
         * @namespace
         */
        const performance = {};

        performance.v1 = (function() {

            /**
             * Namespace v1.
             * @memberof telepact.performance
             * @namespace
             */
            const v1 = {};

            v1.TypicalItem = (function() {

                /**
                 * Properties of a TypicalItem.
                 * @memberof telepact.performance.v1
                 * @interface ITypicalItem
                 * @property {number|Long|null} [accountId] TypicalItem accountId
                 * @property {string|null} [customerName] TypicalItem customerName
                 * @property {string|null} [region] TypicalItem region
                 * @property {number|null} [unitPrice] TypicalItem unitPrice
                 * @property {number|Long|null} [quantity] TypicalItem quantity
                 * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding
                 */

                /**
                 * Constructs a new TypicalItem.
                 * @memberof telepact.performance.v1
                 * @classdesc Represents a TypicalItem.
                 * @implements ITypicalItem
                 * @constructor
                 * @param {telepact.performance.v1.ITypicalItem=} [properties] Properties to set
                 * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding
                 */
                function TypicalItem(properties) {
                    if (properties)
                        for (let keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                            if (properties[keys[i]] != null && keys[i] !== "__proto__")
                                this[keys[i]] = properties[keys[i]];
                }

                /**
                 * TypicalItem accountId.
                 * @member {number|Long} accountId
                 * @memberof telepact.performance.v1.TypicalItem
                 * @instance
                 */
                TypicalItem.prototype.accountId = $util.Long ? $util.Long.fromBits(0,0,false) : 0;

                /**
                 * TypicalItem customerName.
                 * @member {string} customerName
                 * @memberof telepact.performance.v1.TypicalItem
                 * @instance
                 */
                TypicalItem.prototype.customerName = "";

                /**
                 * TypicalItem region.
                 * @member {string} region
                 * @memberof telepact.performance.v1.TypicalItem
                 * @instance
                 */
                TypicalItem.prototype.region = "";

                /**
                 * TypicalItem unitPrice.
                 * @member {number} unitPrice
                 * @memberof telepact.performance.v1.TypicalItem
                 * @instance
                 */
                TypicalItem.prototype.unitPrice = 0;

                /**
                 * TypicalItem quantity.
                 * @member {number|Long} quantity
                 * @memberof telepact.performance.v1.TypicalItem
                 * @instance
                 */
                TypicalItem.prototype.quantity = $util.Long ? $util.Long.fromBits(0,0,false) : 0;

                /**
                 * Creates a new TypicalItem instance using the specified properties.
                 * @function create
                 * @memberof telepact.performance.v1.TypicalItem
                 * @static
                 * @param {telepact.performance.v1.ITypicalItem=} [properties] Properties to set
                 * @returns {telepact.performance.v1.TypicalItem} TypicalItem instance
                 */
                TypicalItem.create = function create(properties) {
                    return new TypicalItem(properties);
                };

                /**
                 * Encodes the specified TypicalItem message. Does not implicitly {@link telepact.performance.v1.TypicalItem.verify|verify} messages.
                 * @function encode
                 * @memberof telepact.performance.v1.TypicalItem
                 * @static
                 * @param {telepact.performance.v1.ITypicalItem} message TypicalItem message or plain object to encode
                 * @param {$protobuf.Writer} [writer] Writer to encode to
                 * @returns {$protobuf.Writer} Writer
                 */
                TypicalItem.encode = function encode(message, writer) {
                    if (!writer)
                        writer = $Writer.create();
                    if (message.accountId != null && Object.hasOwnProperty.call(message, "accountId"))
                        writer.uint32(/* id 1, wireType 0 =*/8).int64(message.accountId);
                    if (message.customerName != null && Object.hasOwnProperty.call(message, "customerName"))
                        writer.uint32(/* id 2, wireType 2 =*/18).string(message.customerName);
                    if (message.region != null && Object.hasOwnProperty.call(message, "region"))
                        writer.uint32(/* id 3, wireType 2 =*/26).string(message.region);
                    if (message.unitPrice != null && Object.hasOwnProperty.call(message, "unitPrice"))
                        writer.uint32(/* id 4, wireType 1 =*/33).double(message.unitPrice);
                    if (message.quantity != null && Object.hasOwnProperty.call(message, "quantity"))
                        writer.uint32(/* id 5, wireType 0 =*/40).int64(message.quantity);
                    if (message.$unknowns != null && Object.hasOwnProperty.call(message, "$unknowns"))
                        for (let i = 0; i < message.$unknowns.length; ++i)
                            writer.raw(message.$unknowns[i]);
                    return writer;
                };

                /**
                 * Encodes the specified TypicalItem message, length delimited. Does not implicitly {@link telepact.performance.v1.TypicalItem.verify|verify} messages.
                 * @function encodeDelimited
                 * @memberof telepact.performance.v1.TypicalItem
                 * @static
                 * @param {telepact.performance.v1.ITypicalItem} message TypicalItem message or plain object to encode
                 * @param {$protobuf.Writer} [writer] Writer to encode to
                 * @returns {$protobuf.Writer} Writer
                 */
                TypicalItem.encodeDelimited = function encodeDelimited(message, writer) {
                    return this.encode(message, writer).ldelim();
                };

                /**
                 * Decodes a TypicalItem message from the specified reader or buffer.
                 * @function decode
                 * @memberof telepact.performance.v1.TypicalItem
                 * @static
                 * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
                 * @param {number} [length] Message length if known beforehand
                 * @returns {telepact.performance.v1.TypicalItem} TypicalItem
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                TypicalItem.decode = function decode(reader, length, _end, _depth, _target) {
                    if (!(reader instanceof $Reader))
                        reader = $Reader.create(reader);
                    if (_depth === undefined)
                        _depth = 0;
                    if (_depth > $Reader.recursionLimit)
                        throw Error("max depth exceeded");
                    let end = length === undefined ? reader.len : reader.pos + length, message = _target || new $root.telepact.performance.v1.TypicalItem(), value;
                    while (reader.pos < end) {
                        let start = reader.pos;
                        let tag = reader.tag();
                        if (tag === _end) {
                            _end = undefined;
                            break;
                        }
                        let wireType = tag & 7;
                        switch (tag >>>= 3) {
                        case 1: {
                                if (wireType !== 0)
                                    break;
                                if (typeof (value = reader.int64()) === "object" ? value.low || value.high : value !== 0)
                                    message.accountId = value;
                                else
                                    delete message.accountId;
                                continue;
                            }
                        case 2: {
                                if (wireType !== 2)
                                    break;
                                if ((value = reader.string()).length)
                                    message.customerName = value;
                                else
                                    delete message.customerName;
                                continue;
                            }
                        case 3: {
                                if (wireType !== 2)
                                    break;
                                if ((value = reader.string()).length)
                                    message.region = value;
                                else
                                    delete message.region;
                                continue;
                            }
                        case 4: {
                                if (wireType !== 1)
                                    break;
                                if ((value = reader.double()) !== 0)
                                    message.unitPrice = value;
                                else
                                    delete message.unitPrice;
                                continue;
                            }
                        case 5: {
                                if (wireType !== 0)
                                    break;
                                if (typeof (value = reader.int64()) === "object" ? value.low || value.high : value !== 0)
                                    message.quantity = value;
                                else
                                    delete message.quantity;
                                continue;
                            }
                        }
                        reader.skipType(wireType, _depth, tag);
                        $util.makeProp(message, "$unknowns", false);
                        (message.$unknowns || (message.$unknowns = [])).push(reader.raw(start, reader.pos));
                    }
                    if (_end !== undefined)
                        throw Error("missing end group");
                    return message;
                };

                /**
                 * Decodes a TypicalItem message from the specified reader or buffer, length delimited.
                 * @function decodeDelimited
                 * @memberof telepact.performance.v1.TypicalItem
                 * @static
                 * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
                 * @returns {telepact.performance.v1.TypicalItem} TypicalItem
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                TypicalItem.decodeDelimited = function decodeDelimited(reader) {
                    if (!(reader instanceof $Reader))
                        reader = new $Reader(reader);
                    return this.decode(reader, reader.uint32());
                };

                /**
                 * Verifies a TypicalItem message.
                 * @function verify
                 * @memberof telepact.performance.v1.TypicalItem
                 * @static
                 * @param {Object.<string,*>} message Plain object to verify
                 * @returns {string|null} `null` if valid, otherwise the reason why it is not
                 */
                TypicalItem.verify = function verify(message, _depth) {
                    if (typeof message !== "object" || message === null)
                        return "object expected";
                    if (_depth === undefined)
                        _depth = 0;
                    if (_depth > $util.recursionLimit)
                        return "max depth exceeded";
                    if (message.accountId != null && message.hasOwnProperty("accountId"))
                        if (!$util.isInteger(message.accountId) && !(message.accountId && $util.isInteger(message.accountId.low) && $util.isInteger(message.accountId.high)))
                            return "accountId: integer|Long expected";
                    if (message.customerName != null && message.hasOwnProperty("customerName"))
                        if (!$util.isString(message.customerName))
                            return "customerName: string expected";
                    if (message.region != null && message.hasOwnProperty("region"))
                        if (!$util.isString(message.region))
                            return "region: string expected";
                    if (message.unitPrice != null && message.hasOwnProperty("unitPrice"))
                        if (typeof message.unitPrice !== "number")
                            return "unitPrice: number expected";
                    if (message.quantity != null && message.hasOwnProperty("quantity"))
                        if (!$util.isInteger(message.quantity) && !(message.quantity && $util.isInteger(message.quantity.low) && $util.isInteger(message.quantity.high)))
                            return "quantity: integer|Long expected";
                    return null;
                };

                /**
                 * Creates a TypicalItem message from a plain object. Also converts values to their respective internal types.
                 * @function fromObject
                 * @memberof telepact.performance.v1.TypicalItem
                 * @static
                 * @param {Object.<string,*>} object Plain object
                 * @returns {telepact.performance.v1.TypicalItem} TypicalItem
                 */
                TypicalItem.fromObject = function fromObject(object, _depth) {
                    if (object instanceof $root.telepact.performance.v1.TypicalItem)
                        return object;
                    if (_depth === undefined)
                        _depth = 0;
                    if (_depth > $util.recursionLimit)
                        throw Error("max depth exceeded");
                    let message = new $root.telepact.performance.v1.TypicalItem();
                    if (object.accountId != null)
                        if (typeof object.accountId === "object" ? object.accountId.low || object.accountId.high : Number(object.accountId) !== 0)
                            if ($util.Long)
                                (message.accountId = $util.Long.fromValue(object.accountId)).unsigned = false;
                            else if (typeof object.accountId === "string")
                                message.accountId = parseInt(object.accountId, 10);
                            else if (typeof object.accountId === "number")
                                message.accountId = object.accountId;
                            else if (typeof object.accountId === "object")
                                message.accountId = new $util.LongBits(object.accountId.low >>> 0, object.accountId.high >>> 0).toNumber();
                    if (object.customerName != null)
                        if (typeof object.customerName !== "string" || object.customerName.length)
                            message.customerName = String(object.customerName);
                    if (object.region != null)
                        if (typeof object.region !== "string" || object.region.length)
                            message.region = String(object.region);
                    if (object.unitPrice != null)
                        if (Number(object.unitPrice) !== 0)
                            message.unitPrice = Number(object.unitPrice);
                    if (object.quantity != null)
                        if (typeof object.quantity === "object" ? object.quantity.low || object.quantity.high : Number(object.quantity) !== 0)
                            if ($util.Long)
                                (message.quantity = $util.Long.fromValue(object.quantity)).unsigned = false;
                            else if (typeof object.quantity === "string")
                                message.quantity = parseInt(object.quantity, 10);
                            else if (typeof object.quantity === "number")
                                message.quantity = object.quantity;
                            else if (typeof object.quantity === "object")
                                message.quantity = new $util.LongBits(object.quantity.low >>> 0, object.quantity.high >>> 0).toNumber();
                    return message;
                };

                /**
                 * Creates a plain object from a TypicalItem message. Also converts values to other types if specified.
                 * @function toObject
                 * @memberof telepact.performance.v1.TypicalItem
                 * @static
                 * @param {telepact.performance.v1.TypicalItem} message TypicalItem
                 * @param {$protobuf.IConversionOptions} [options] Conversion options
                 * @returns {Object.<string,*>} Plain object
                 */
                TypicalItem.toObject = function toObject(message, options) {
                    if (!options)
                        options = {};
                    let object = {};
                    if (options.defaults) {
                        if ($util.Long) {
                            let long = new $util.Long(0, 0, false);
                            object.accountId = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : long;
                        } else
                            object.accountId = options.longs === String ? "0" : 0;
                        object.customerName = "";
                        object.region = "";
                        object.unitPrice = 0;
                        if ($util.Long) {
                            let long = new $util.Long(0, 0, false);
                            object.quantity = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : long;
                        } else
                            object.quantity = options.longs === String ? "0" : 0;
                    }
                    if (message.accountId != null && message.hasOwnProperty("accountId"))
                        if (typeof message.accountId === "number")
                            object.accountId = options.longs === String ? String(message.accountId) : message.accountId;
                        else
                            object.accountId = options.longs === String ? $util.Long.prototype.toString.call(message.accountId) : options.longs === Number ? new $util.LongBits(message.accountId.low >>> 0, message.accountId.high >>> 0).toNumber() : message.accountId;
                    if (message.customerName != null && message.hasOwnProperty("customerName"))
                        object.customerName = message.customerName;
                    if (message.region != null && message.hasOwnProperty("region"))
                        object.region = message.region;
                    if (message.unitPrice != null && message.hasOwnProperty("unitPrice"))
                        object.unitPrice = options.json && !isFinite(message.unitPrice) ? String(message.unitPrice) : message.unitPrice;
                    if (message.quantity != null && message.hasOwnProperty("quantity"))
                        if (typeof message.quantity === "number")
                            object.quantity = options.longs === String ? String(message.quantity) : message.quantity;
                        else
                            object.quantity = options.longs === String ? $util.Long.prototype.toString.call(message.quantity) : options.longs === Number ? new $util.LongBits(message.quantity.low >>> 0, message.quantity.high >>> 0).toNumber() : message.quantity;
                    return object;
                };

                /**
                 * Converts this TypicalItem to JSON.
                 * @function toJSON
                 * @memberof telepact.performance.v1.TypicalItem
                 * @instance
                 * @returns {Object.<string,*>} JSON object
                 */
                TypicalItem.prototype.toJSON = function toJSON() {
                    return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
                };

                /**
                 * Gets the type url for TypicalItem
                 * @function getTypeUrl
                 * @memberof telepact.performance.v1.TypicalItem
                 * @static
                 * @param {string} [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
                 * @returns {string} The type url
                 */
                TypicalItem.getTypeUrl = function getTypeUrl(prefix) {
                    if (prefix === undefined)
                        prefix = "type.googleapis.com";
                    return prefix + "/telepact.performance.v1.TypicalItem";
                };

                return TypicalItem;
            })();

            v1.StringItem = (function() {

                /**
                 * Properties of a StringItem.
                 * @memberof telepact.performance.v1
                 * @interface IStringItem
                 * @property {string|null} [code] StringItem code
                 * @property {string|null} [city] StringItem city
                 * @property {string|null} [country] StringItem country
                 * @property {string|null} [segment] StringItem segment
                 * @property {string|null} [status] StringItem status
                 * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding
                 */

                /**
                 * Constructs a new StringItem.
                 * @memberof telepact.performance.v1
                 * @classdesc Represents a StringItem.
                 * @implements IStringItem
                 * @constructor
                 * @param {telepact.performance.v1.IStringItem=} [properties] Properties to set
                 * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding
                 */
                function StringItem(properties) {
                    if (properties)
                        for (let keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                            if (properties[keys[i]] != null && keys[i] !== "__proto__")
                                this[keys[i]] = properties[keys[i]];
                }

                /**
                 * StringItem code.
                 * @member {string} code
                 * @memberof telepact.performance.v1.StringItem
                 * @instance
                 */
                StringItem.prototype.code = "";

                /**
                 * StringItem city.
                 * @member {string} city
                 * @memberof telepact.performance.v1.StringItem
                 * @instance
                 */
                StringItem.prototype.city = "";

                /**
                 * StringItem country.
                 * @member {string} country
                 * @memberof telepact.performance.v1.StringItem
                 * @instance
                 */
                StringItem.prototype.country = "";

                /**
                 * StringItem segment.
                 * @member {string} segment
                 * @memberof telepact.performance.v1.StringItem
                 * @instance
                 */
                StringItem.prototype.segment = "";

                /**
                 * StringItem status.
                 * @member {string} status
                 * @memberof telepact.performance.v1.StringItem
                 * @instance
                 */
                StringItem.prototype.status = "";

                /**
                 * Creates a new StringItem instance using the specified properties.
                 * @function create
                 * @memberof telepact.performance.v1.StringItem
                 * @static
                 * @param {telepact.performance.v1.IStringItem=} [properties] Properties to set
                 * @returns {telepact.performance.v1.StringItem} StringItem instance
                 */
                StringItem.create = function create(properties) {
                    return new StringItem(properties);
                };

                /**
                 * Encodes the specified StringItem message. Does not implicitly {@link telepact.performance.v1.StringItem.verify|verify} messages.
                 * @function encode
                 * @memberof telepact.performance.v1.StringItem
                 * @static
                 * @param {telepact.performance.v1.IStringItem} message StringItem message or plain object to encode
                 * @param {$protobuf.Writer} [writer] Writer to encode to
                 * @returns {$protobuf.Writer} Writer
                 */
                StringItem.encode = function encode(message, writer) {
                    if (!writer)
                        writer = $Writer.create();
                    if (message.code != null && Object.hasOwnProperty.call(message, "code"))
                        writer.uint32(/* id 1, wireType 2 =*/10).string(message.code);
                    if (message.city != null && Object.hasOwnProperty.call(message, "city"))
                        writer.uint32(/* id 2, wireType 2 =*/18).string(message.city);
                    if (message.country != null && Object.hasOwnProperty.call(message, "country"))
                        writer.uint32(/* id 3, wireType 2 =*/26).string(message.country);
                    if (message.segment != null && Object.hasOwnProperty.call(message, "segment"))
                        writer.uint32(/* id 4, wireType 2 =*/34).string(message.segment);
                    if (message.status != null && Object.hasOwnProperty.call(message, "status"))
                        writer.uint32(/* id 5, wireType 2 =*/42).string(message.status);
                    if (message.$unknowns != null && Object.hasOwnProperty.call(message, "$unknowns"))
                        for (let i = 0; i < message.$unknowns.length; ++i)
                            writer.raw(message.$unknowns[i]);
                    return writer;
                };

                /**
                 * Encodes the specified StringItem message, length delimited. Does not implicitly {@link telepact.performance.v1.StringItem.verify|verify} messages.
                 * @function encodeDelimited
                 * @memberof telepact.performance.v1.StringItem
                 * @static
                 * @param {telepact.performance.v1.IStringItem} message StringItem message or plain object to encode
                 * @param {$protobuf.Writer} [writer] Writer to encode to
                 * @returns {$protobuf.Writer} Writer
                 */
                StringItem.encodeDelimited = function encodeDelimited(message, writer) {
                    return this.encode(message, writer).ldelim();
                };

                /**
                 * Decodes a StringItem message from the specified reader or buffer.
                 * @function decode
                 * @memberof telepact.performance.v1.StringItem
                 * @static
                 * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
                 * @param {number} [length] Message length if known beforehand
                 * @returns {telepact.performance.v1.StringItem} StringItem
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                StringItem.decode = function decode(reader, length, _end, _depth, _target) {
                    if (!(reader instanceof $Reader))
                        reader = $Reader.create(reader);
                    if (_depth === undefined)
                        _depth = 0;
                    if (_depth > $Reader.recursionLimit)
                        throw Error("max depth exceeded");
                    let end = length === undefined ? reader.len : reader.pos + length, message = _target || new $root.telepact.performance.v1.StringItem(), value;
                    while (reader.pos < end) {
                        let start = reader.pos;
                        let tag = reader.tag();
                        if (tag === _end) {
                            _end = undefined;
                            break;
                        }
                        let wireType = tag & 7;
                        switch (tag >>>= 3) {
                        case 1: {
                                if (wireType !== 2)
                                    break;
                                if ((value = reader.string()).length)
                                    message.code = value;
                                else
                                    delete message.code;
                                continue;
                            }
                        case 2: {
                                if (wireType !== 2)
                                    break;
                                if ((value = reader.string()).length)
                                    message.city = value;
                                else
                                    delete message.city;
                                continue;
                            }
                        case 3: {
                                if (wireType !== 2)
                                    break;
                                if ((value = reader.string()).length)
                                    message.country = value;
                                else
                                    delete message.country;
                                continue;
                            }
                        case 4: {
                                if (wireType !== 2)
                                    break;
                                if ((value = reader.string()).length)
                                    message.segment = value;
                                else
                                    delete message.segment;
                                continue;
                            }
                        case 5: {
                                if (wireType !== 2)
                                    break;
                                if ((value = reader.string()).length)
                                    message.status = value;
                                else
                                    delete message.status;
                                continue;
                            }
                        }
                        reader.skipType(wireType, _depth, tag);
                        $util.makeProp(message, "$unknowns", false);
                        (message.$unknowns || (message.$unknowns = [])).push(reader.raw(start, reader.pos));
                    }
                    if (_end !== undefined)
                        throw Error("missing end group");
                    return message;
                };

                /**
                 * Decodes a StringItem message from the specified reader or buffer, length delimited.
                 * @function decodeDelimited
                 * @memberof telepact.performance.v1.StringItem
                 * @static
                 * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
                 * @returns {telepact.performance.v1.StringItem} StringItem
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                StringItem.decodeDelimited = function decodeDelimited(reader) {
                    if (!(reader instanceof $Reader))
                        reader = new $Reader(reader);
                    return this.decode(reader, reader.uint32());
                };

                /**
                 * Verifies a StringItem message.
                 * @function verify
                 * @memberof telepact.performance.v1.StringItem
                 * @static
                 * @param {Object.<string,*>} message Plain object to verify
                 * @returns {string|null} `null` if valid, otherwise the reason why it is not
                 */
                StringItem.verify = function verify(message, _depth) {
                    if (typeof message !== "object" || message === null)
                        return "object expected";
                    if (_depth === undefined)
                        _depth = 0;
                    if (_depth > $util.recursionLimit)
                        return "max depth exceeded";
                    if (message.code != null && message.hasOwnProperty("code"))
                        if (!$util.isString(message.code))
                            return "code: string expected";
                    if (message.city != null && message.hasOwnProperty("city"))
                        if (!$util.isString(message.city))
                            return "city: string expected";
                    if (message.country != null && message.hasOwnProperty("country"))
                        if (!$util.isString(message.country))
                            return "country: string expected";
                    if (message.segment != null && message.hasOwnProperty("segment"))
                        if (!$util.isString(message.segment))
                            return "segment: string expected";
                    if (message.status != null && message.hasOwnProperty("status"))
                        if (!$util.isString(message.status))
                            return "status: string expected";
                    return null;
                };

                /**
                 * Creates a StringItem message from a plain object. Also converts values to their respective internal types.
                 * @function fromObject
                 * @memberof telepact.performance.v1.StringItem
                 * @static
                 * @param {Object.<string,*>} object Plain object
                 * @returns {telepact.performance.v1.StringItem} StringItem
                 */
                StringItem.fromObject = function fromObject(object, _depth) {
                    if (object instanceof $root.telepact.performance.v1.StringItem)
                        return object;
                    if (_depth === undefined)
                        _depth = 0;
                    if (_depth > $util.recursionLimit)
                        throw Error("max depth exceeded");
                    let message = new $root.telepact.performance.v1.StringItem();
                    if (object.code != null)
                        if (typeof object.code !== "string" || object.code.length)
                            message.code = String(object.code);
                    if (object.city != null)
                        if (typeof object.city !== "string" || object.city.length)
                            message.city = String(object.city);
                    if (object.country != null)
                        if (typeof object.country !== "string" || object.country.length)
                            message.country = String(object.country);
                    if (object.segment != null)
                        if (typeof object.segment !== "string" || object.segment.length)
                            message.segment = String(object.segment);
                    if (object.status != null)
                        if (typeof object.status !== "string" || object.status.length)
                            message.status = String(object.status);
                    return message;
                };

                /**
                 * Creates a plain object from a StringItem message. Also converts values to other types if specified.
                 * @function toObject
                 * @memberof telepact.performance.v1.StringItem
                 * @static
                 * @param {telepact.performance.v1.StringItem} message StringItem
                 * @param {$protobuf.IConversionOptions} [options] Conversion options
                 * @returns {Object.<string,*>} Plain object
                 */
                StringItem.toObject = function toObject(message, options) {
                    if (!options)
                        options = {};
                    let object = {};
                    if (options.defaults) {
                        object.code = "";
                        object.city = "";
                        object.country = "";
                        object.segment = "";
                        object.status = "";
                    }
                    if (message.code != null && message.hasOwnProperty("code"))
                        object.code = message.code;
                    if (message.city != null && message.hasOwnProperty("city"))
                        object.city = message.city;
                    if (message.country != null && message.hasOwnProperty("country"))
                        object.country = message.country;
                    if (message.segment != null && message.hasOwnProperty("segment"))
                        object.segment = message.segment;
                    if (message.status != null && message.hasOwnProperty("status"))
                        object.status = message.status;
                    return object;
                };

                /**
                 * Converts this StringItem to JSON.
                 * @function toJSON
                 * @memberof telepact.performance.v1.StringItem
                 * @instance
                 * @returns {Object.<string,*>} JSON object
                 */
                StringItem.prototype.toJSON = function toJSON() {
                    return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
                };

                /**
                 * Gets the type url for StringItem
                 * @function getTypeUrl
                 * @memberof telepact.performance.v1.StringItem
                 * @static
                 * @param {string} [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
                 * @returns {string} The type url
                 */
                StringItem.getTypeUrl = function getTypeUrl(prefix) {
                    if (prefix === undefined)
                        prefix = "type.googleapis.com";
                    return prefix + "/telepact.performance.v1.StringItem";
                };

                return StringItem;
            })();

            v1.NumberItem = (function() {

                /**
                 * Properties of a NumberItem.
                 * @memberof telepact.performance.v1
                 * @interface INumberItem
                 * @property {number|Long|null} [accountId] NumberItem accountId
                 * @property {number|Long|null} [visits] NumberItem visits
                 * @property {number|null} [score] NumberItem score
                 * @property {number|null} [balance] NumberItem balance
                 * @property {number|null} [ratio] NumberItem ratio
                 * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding
                 */

                /**
                 * Constructs a new NumberItem.
                 * @memberof telepact.performance.v1
                 * @classdesc Represents a NumberItem.
                 * @implements INumberItem
                 * @constructor
                 * @param {telepact.performance.v1.INumberItem=} [properties] Properties to set
                 * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding
                 */
                function NumberItem(properties) {
                    if (properties)
                        for (let keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                            if (properties[keys[i]] != null && keys[i] !== "__proto__")
                                this[keys[i]] = properties[keys[i]];
                }

                /**
                 * NumberItem accountId.
                 * @member {number|Long} accountId
                 * @memberof telepact.performance.v1.NumberItem
                 * @instance
                 */
                NumberItem.prototype.accountId = $util.Long ? $util.Long.fromBits(0,0,false) : 0;

                /**
                 * NumberItem visits.
                 * @member {number|Long} visits
                 * @memberof telepact.performance.v1.NumberItem
                 * @instance
                 */
                NumberItem.prototype.visits = $util.Long ? $util.Long.fromBits(0,0,false) : 0;

                /**
                 * NumberItem score.
                 * @member {number} score
                 * @memberof telepact.performance.v1.NumberItem
                 * @instance
                 */
                NumberItem.prototype.score = 0;

                /**
                 * NumberItem balance.
                 * @member {number} balance
                 * @memberof telepact.performance.v1.NumberItem
                 * @instance
                 */
                NumberItem.prototype.balance = 0;

                /**
                 * NumberItem ratio.
                 * @member {number} ratio
                 * @memberof telepact.performance.v1.NumberItem
                 * @instance
                 */
                NumberItem.prototype.ratio = 0;

                /**
                 * Creates a new NumberItem instance using the specified properties.
                 * @function create
                 * @memberof telepact.performance.v1.NumberItem
                 * @static
                 * @param {telepact.performance.v1.INumberItem=} [properties] Properties to set
                 * @returns {telepact.performance.v1.NumberItem} NumberItem instance
                 */
                NumberItem.create = function create(properties) {
                    return new NumberItem(properties);
                };

                /**
                 * Encodes the specified NumberItem message. Does not implicitly {@link telepact.performance.v1.NumberItem.verify|verify} messages.
                 * @function encode
                 * @memberof telepact.performance.v1.NumberItem
                 * @static
                 * @param {telepact.performance.v1.INumberItem} message NumberItem message or plain object to encode
                 * @param {$protobuf.Writer} [writer] Writer to encode to
                 * @returns {$protobuf.Writer} Writer
                 */
                NumberItem.encode = function encode(message, writer) {
                    if (!writer)
                        writer = $Writer.create();
                    if (message.accountId != null && Object.hasOwnProperty.call(message, "accountId"))
                        writer.uint32(/* id 1, wireType 0 =*/8).int64(message.accountId);
                    if (message.visits != null && Object.hasOwnProperty.call(message, "visits"))
                        writer.uint32(/* id 2, wireType 0 =*/16).int64(message.visits);
                    if (message.score != null && Object.hasOwnProperty.call(message, "score"))
                        writer.uint32(/* id 3, wireType 1 =*/25).double(message.score);
                    if (message.balance != null && Object.hasOwnProperty.call(message, "balance"))
                        writer.uint32(/* id 4, wireType 1 =*/33).double(message.balance);
                    if (message.ratio != null && Object.hasOwnProperty.call(message, "ratio"))
                        writer.uint32(/* id 5, wireType 1 =*/41).double(message.ratio);
                    if (message.$unknowns != null && Object.hasOwnProperty.call(message, "$unknowns"))
                        for (let i = 0; i < message.$unknowns.length; ++i)
                            writer.raw(message.$unknowns[i]);
                    return writer;
                };

                /**
                 * Encodes the specified NumberItem message, length delimited. Does not implicitly {@link telepact.performance.v1.NumberItem.verify|verify} messages.
                 * @function encodeDelimited
                 * @memberof telepact.performance.v1.NumberItem
                 * @static
                 * @param {telepact.performance.v1.INumberItem} message NumberItem message or plain object to encode
                 * @param {$protobuf.Writer} [writer] Writer to encode to
                 * @returns {$protobuf.Writer} Writer
                 */
                NumberItem.encodeDelimited = function encodeDelimited(message, writer) {
                    return this.encode(message, writer).ldelim();
                };

                /**
                 * Decodes a NumberItem message from the specified reader or buffer.
                 * @function decode
                 * @memberof telepact.performance.v1.NumberItem
                 * @static
                 * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
                 * @param {number} [length] Message length if known beforehand
                 * @returns {telepact.performance.v1.NumberItem} NumberItem
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                NumberItem.decode = function decode(reader, length, _end, _depth, _target) {
                    if (!(reader instanceof $Reader))
                        reader = $Reader.create(reader);
                    if (_depth === undefined)
                        _depth = 0;
                    if (_depth > $Reader.recursionLimit)
                        throw Error("max depth exceeded");
                    let end = length === undefined ? reader.len : reader.pos + length, message = _target || new $root.telepact.performance.v1.NumberItem(), value;
                    while (reader.pos < end) {
                        let start = reader.pos;
                        let tag = reader.tag();
                        if (tag === _end) {
                            _end = undefined;
                            break;
                        }
                        let wireType = tag & 7;
                        switch (tag >>>= 3) {
                        case 1: {
                                if (wireType !== 0)
                                    break;
                                if (typeof (value = reader.int64()) === "object" ? value.low || value.high : value !== 0)
                                    message.accountId = value;
                                else
                                    delete message.accountId;
                                continue;
                            }
                        case 2: {
                                if (wireType !== 0)
                                    break;
                                if (typeof (value = reader.int64()) === "object" ? value.low || value.high : value !== 0)
                                    message.visits = value;
                                else
                                    delete message.visits;
                                continue;
                            }
                        case 3: {
                                if (wireType !== 1)
                                    break;
                                if ((value = reader.double()) !== 0)
                                    message.score = value;
                                else
                                    delete message.score;
                                continue;
                            }
                        case 4: {
                                if (wireType !== 1)
                                    break;
                                if ((value = reader.double()) !== 0)
                                    message.balance = value;
                                else
                                    delete message.balance;
                                continue;
                            }
                        case 5: {
                                if (wireType !== 1)
                                    break;
                                if ((value = reader.double()) !== 0)
                                    message.ratio = value;
                                else
                                    delete message.ratio;
                                continue;
                            }
                        }
                        reader.skipType(wireType, _depth, tag);
                        $util.makeProp(message, "$unknowns", false);
                        (message.$unknowns || (message.$unknowns = [])).push(reader.raw(start, reader.pos));
                    }
                    if (_end !== undefined)
                        throw Error("missing end group");
                    return message;
                };

                /**
                 * Decodes a NumberItem message from the specified reader or buffer, length delimited.
                 * @function decodeDelimited
                 * @memberof telepact.performance.v1.NumberItem
                 * @static
                 * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
                 * @returns {telepact.performance.v1.NumberItem} NumberItem
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                NumberItem.decodeDelimited = function decodeDelimited(reader) {
                    if (!(reader instanceof $Reader))
                        reader = new $Reader(reader);
                    return this.decode(reader, reader.uint32());
                };

                /**
                 * Verifies a NumberItem message.
                 * @function verify
                 * @memberof telepact.performance.v1.NumberItem
                 * @static
                 * @param {Object.<string,*>} message Plain object to verify
                 * @returns {string|null} `null` if valid, otherwise the reason why it is not
                 */
                NumberItem.verify = function verify(message, _depth) {
                    if (typeof message !== "object" || message === null)
                        return "object expected";
                    if (_depth === undefined)
                        _depth = 0;
                    if (_depth > $util.recursionLimit)
                        return "max depth exceeded";
                    if (message.accountId != null && message.hasOwnProperty("accountId"))
                        if (!$util.isInteger(message.accountId) && !(message.accountId && $util.isInteger(message.accountId.low) && $util.isInteger(message.accountId.high)))
                            return "accountId: integer|Long expected";
                    if (message.visits != null && message.hasOwnProperty("visits"))
                        if (!$util.isInteger(message.visits) && !(message.visits && $util.isInteger(message.visits.low) && $util.isInteger(message.visits.high)))
                            return "visits: integer|Long expected";
                    if (message.score != null && message.hasOwnProperty("score"))
                        if (typeof message.score !== "number")
                            return "score: number expected";
                    if (message.balance != null && message.hasOwnProperty("balance"))
                        if (typeof message.balance !== "number")
                            return "balance: number expected";
                    if (message.ratio != null && message.hasOwnProperty("ratio"))
                        if (typeof message.ratio !== "number")
                            return "ratio: number expected";
                    return null;
                };

                /**
                 * Creates a NumberItem message from a plain object. Also converts values to their respective internal types.
                 * @function fromObject
                 * @memberof telepact.performance.v1.NumberItem
                 * @static
                 * @param {Object.<string,*>} object Plain object
                 * @returns {telepact.performance.v1.NumberItem} NumberItem
                 */
                NumberItem.fromObject = function fromObject(object, _depth) {
                    if (object instanceof $root.telepact.performance.v1.NumberItem)
                        return object;
                    if (_depth === undefined)
                        _depth = 0;
                    if (_depth > $util.recursionLimit)
                        throw Error("max depth exceeded");
                    let message = new $root.telepact.performance.v1.NumberItem();
                    if (object.accountId != null)
                        if (typeof object.accountId === "object" ? object.accountId.low || object.accountId.high : Number(object.accountId) !== 0)
                            if ($util.Long)
                                (message.accountId = $util.Long.fromValue(object.accountId)).unsigned = false;
                            else if (typeof object.accountId === "string")
                                message.accountId = parseInt(object.accountId, 10);
                            else if (typeof object.accountId === "number")
                                message.accountId = object.accountId;
                            else if (typeof object.accountId === "object")
                                message.accountId = new $util.LongBits(object.accountId.low >>> 0, object.accountId.high >>> 0).toNumber();
                    if (object.visits != null)
                        if (typeof object.visits === "object" ? object.visits.low || object.visits.high : Number(object.visits) !== 0)
                            if ($util.Long)
                                (message.visits = $util.Long.fromValue(object.visits)).unsigned = false;
                            else if (typeof object.visits === "string")
                                message.visits = parseInt(object.visits, 10);
                            else if (typeof object.visits === "number")
                                message.visits = object.visits;
                            else if (typeof object.visits === "object")
                                message.visits = new $util.LongBits(object.visits.low >>> 0, object.visits.high >>> 0).toNumber();
                    if (object.score != null)
                        if (Number(object.score) !== 0)
                            message.score = Number(object.score);
                    if (object.balance != null)
                        if (Number(object.balance) !== 0)
                            message.balance = Number(object.balance);
                    if (object.ratio != null)
                        if (Number(object.ratio) !== 0)
                            message.ratio = Number(object.ratio);
                    return message;
                };

                /**
                 * Creates a plain object from a NumberItem message. Also converts values to other types if specified.
                 * @function toObject
                 * @memberof telepact.performance.v1.NumberItem
                 * @static
                 * @param {telepact.performance.v1.NumberItem} message NumberItem
                 * @param {$protobuf.IConversionOptions} [options] Conversion options
                 * @returns {Object.<string,*>} Plain object
                 */
                NumberItem.toObject = function toObject(message, options) {
                    if (!options)
                        options = {};
                    let object = {};
                    if (options.defaults) {
                        if ($util.Long) {
                            let long = new $util.Long(0, 0, false);
                            object.accountId = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : long;
                        } else
                            object.accountId = options.longs === String ? "0" : 0;
                        if ($util.Long) {
                            let long = new $util.Long(0, 0, false);
                            object.visits = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : long;
                        } else
                            object.visits = options.longs === String ? "0" : 0;
                        object.score = 0;
                        object.balance = 0;
                        object.ratio = 0;
                    }
                    if (message.accountId != null && message.hasOwnProperty("accountId"))
                        if (typeof message.accountId === "number")
                            object.accountId = options.longs === String ? String(message.accountId) : message.accountId;
                        else
                            object.accountId = options.longs === String ? $util.Long.prototype.toString.call(message.accountId) : options.longs === Number ? new $util.LongBits(message.accountId.low >>> 0, message.accountId.high >>> 0).toNumber() : message.accountId;
                    if (message.visits != null && message.hasOwnProperty("visits"))
                        if (typeof message.visits === "number")
                            object.visits = options.longs === String ? String(message.visits) : message.visits;
                        else
                            object.visits = options.longs === String ? $util.Long.prototype.toString.call(message.visits) : options.longs === Number ? new $util.LongBits(message.visits.low >>> 0, message.visits.high >>> 0).toNumber() : message.visits;
                    if (message.score != null && message.hasOwnProperty("score"))
                        object.score = options.json && !isFinite(message.score) ? String(message.score) : message.score;
                    if (message.balance != null && message.hasOwnProperty("balance"))
                        object.balance = options.json && !isFinite(message.balance) ? String(message.balance) : message.balance;
                    if (message.ratio != null && message.hasOwnProperty("ratio"))
                        object.ratio = options.json && !isFinite(message.ratio) ? String(message.ratio) : message.ratio;
                    return object;
                };

                /**
                 * Converts this NumberItem to JSON.
                 * @function toJSON
                 * @memberof telepact.performance.v1.NumberItem
                 * @instance
                 * @returns {Object.<string,*>} JSON object
                 */
                NumberItem.prototype.toJSON = function toJSON() {
                    return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
                };

                /**
                 * Gets the type url for NumberItem
                 * @function getTypeUrl
                 * @memberof telepact.performance.v1.NumberItem
                 * @static
                 * @param {string} [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
                 * @returns {string} The type url
                 */
                NumberItem.getTypeUrl = function getTypeUrl(prefix) {
                    if (prefix === undefined)
                        prefix = "type.googleapis.com";
                    return prefix + "/telepact.performance.v1.NumberItem";
                };

                return NumberItem;
            })();

            v1.TypicalRequest = (function() {

                /**
                 * Properties of a TypicalRequest.
                 * @memberof telepact.performance.v1
                 * @interface ITypicalRequest
                 * @property {Array.<telepact.performance.v1.ITypicalItem>|null} [items] TypicalRequest items
                 * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding
                 */

                /**
                 * Constructs a new TypicalRequest.
                 * @memberof telepact.performance.v1
                 * @classdesc Represents a TypicalRequest.
                 * @implements ITypicalRequest
                 * @constructor
                 * @param {telepact.performance.v1.ITypicalRequest=} [properties] Properties to set
                 * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding
                 */
                function TypicalRequest(properties) {
                    this.items = [];
                    if (properties)
                        for (let keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                            if (properties[keys[i]] != null && keys[i] !== "__proto__")
                                this[keys[i]] = properties[keys[i]];
                }

                /**
                 * TypicalRequest items.
                 * @member {Array.<telepact.performance.v1.ITypicalItem>} items
                 * @memberof telepact.performance.v1.TypicalRequest
                 * @instance
                 */
                TypicalRequest.prototype.items = $util.emptyArray;

                /**
                 * Creates a new TypicalRequest instance using the specified properties.
                 * @function create
                 * @memberof telepact.performance.v1.TypicalRequest
                 * @static
                 * @param {telepact.performance.v1.ITypicalRequest=} [properties] Properties to set
                 * @returns {telepact.performance.v1.TypicalRequest} TypicalRequest instance
                 */
                TypicalRequest.create = function create(properties) {
                    return new TypicalRequest(properties);
                };

                /**
                 * Encodes the specified TypicalRequest message. Does not implicitly {@link telepact.performance.v1.TypicalRequest.verify|verify} messages.
                 * @function encode
                 * @memberof telepact.performance.v1.TypicalRequest
                 * @static
                 * @param {telepact.performance.v1.ITypicalRequest} message TypicalRequest message or plain object to encode
                 * @param {$protobuf.Writer} [writer] Writer to encode to
                 * @returns {$protobuf.Writer} Writer
                 */
                TypicalRequest.encode = function encode(message, writer) {
                    if (!writer)
                        writer = $Writer.create();
                    if (message.items != null && message.items.length)
                        for (let i = 0; i < message.items.length; ++i)
                            $root.telepact.performance.v1.TypicalItem.encode(message.items[i], writer.uint32(/* id 1, wireType 2 =*/10).fork()).ldelim();
                    if (message.$unknowns != null && Object.hasOwnProperty.call(message, "$unknowns"))
                        for (let i = 0; i < message.$unknowns.length; ++i)
                            writer.raw(message.$unknowns[i]);
                    return writer;
                };

                /**
                 * Encodes the specified TypicalRequest message, length delimited. Does not implicitly {@link telepact.performance.v1.TypicalRequest.verify|verify} messages.
                 * @function encodeDelimited
                 * @memberof telepact.performance.v1.TypicalRequest
                 * @static
                 * @param {telepact.performance.v1.ITypicalRequest} message TypicalRequest message or plain object to encode
                 * @param {$protobuf.Writer} [writer] Writer to encode to
                 * @returns {$protobuf.Writer} Writer
                 */
                TypicalRequest.encodeDelimited = function encodeDelimited(message, writer) {
                    return this.encode(message, writer).ldelim();
                };

                /**
                 * Decodes a TypicalRequest message from the specified reader or buffer.
                 * @function decode
                 * @memberof telepact.performance.v1.TypicalRequest
                 * @static
                 * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
                 * @param {number} [length] Message length if known beforehand
                 * @returns {telepact.performance.v1.TypicalRequest} TypicalRequest
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                TypicalRequest.decode = function decode(reader, length, _end, _depth, _target) {
                    if (!(reader instanceof $Reader))
                        reader = $Reader.create(reader);
                    if (_depth === undefined)
                        _depth = 0;
                    if (_depth > $Reader.recursionLimit)
                        throw Error("max depth exceeded");
                    let end = length === undefined ? reader.len : reader.pos + length, message = _target || new $root.telepact.performance.v1.TypicalRequest();
                    while (reader.pos < end) {
                        let start = reader.pos;
                        let tag = reader.tag();
                        if (tag === _end) {
                            _end = undefined;
                            break;
                        }
                        let wireType = tag & 7;
                        switch (tag >>>= 3) {
                        case 1: {
                                if (wireType !== 2)
                                    break;
                                if (!(message.items && message.items.length))
                                    message.items = [];
                                message.items.push($root.telepact.performance.v1.TypicalItem.decode(reader, reader.uint32(), undefined, _depth + 1));
                                continue;
                            }
                        }
                        reader.skipType(wireType, _depth, tag);
                        $util.makeProp(message, "$unknowns", false);
                        (message.$unknowns || (message.$unknowns = [])).push(reader.raw(start, reader.pos));
                    }
                    if (_end !== undefined)
                        throw Error("missing end group");
                    return message;
                };

                /**
                 * Decodes a TypicalRequest message from the specified reader or buffer, length delimited.
                 * @function decodeDelimited
                 * @memberof telepact.performance.v1.TypicalRequest
                 * @static
                 * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
                 * @returns {telepact.performance.v1.TypicalRequest} TypicalRequest
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                TypicalRequest.decodeDelimited = function decodeDelimited(reader) {
                    if (!(reader instanceof $Reader))
                        reader = new $Reader(reader);
                    return this.decode(reader, reader.uint32());
                };

                /**
                 * Verifies a TypicalRequest message.
                 * @function verify
                 * @memberof telepact.performance.v1.TypicalRequest
                 * @static
                 * @param {Object.<string,*>} message Plain object to verify
                 * @returns {string|null} `null` if valid, otherwise the reason why it is not
                 */
                TypicalRequest.verify = function verify(message, _depth) {
                    if (typeof message !== "object" || message === null)
                        return "object expected";
                    if (_depth === undefined)
                        _depth = 0;
                    if (_depth > $util.recursionLimit)
                        return "max depth exceeded";
                    if (message.items != null && message.hasOwnProperty("items")) {
                        if (!Array.isArray(message.items))
                            return "items: array expected";
                        for (let i = 0; i < message.items.length; ++i) {
                            let error = $root.telepact.performance.v1.TypicalItem.verify(message.items[i], _depth + 1);
                            if (error)
                                return "items." + error;
                        }
                    }
                    return null;
                };

                /**
                 * Creates a TypicalRequest message from a plain object. Also converts values to their respective internal types.
                 * @function fromObject
                 * @memberof telepact.performance.v1.TypicalRequest
                 * @static
                 * @param {Object.<string,*>} object Plain object
                 * @returns {telepact.performance.v1.TypicalRequest} TypicalRequest
                 */
                TypicalRequest.fromObject = function fromObject(object, _depth) {
                    if (object instanceof $root.telepact.performance.v1.TypicalRequest)
                        return object;
                    if (_depth === undefined)
                        _depth = 0;
                    if (_depth > $util.recursionLimit)
                        throw Error("max depth exceeded");
                    let message = new $root.telepact.performance.v1.TypicalRequest();
                    if (object.items) {
                        if (!Array.isArray(object.items))
                            throw TypeError(".telepact.performance.v1.TypicalRequest.items: array expected");
                        message.items = Array(object.items.length);
                        for (let i = 0; i < object.items.length; ++i) {
                            if (typeof object.items[i] !== "object")
                                throw TypeError(".telepact.performance.v1.TypicalRequest.items: object expected");
                            message.items[i] = $root.telepact.performance.v1.TypicalItem.fromObject(object.items[i], _depth + 1);
                        }
                    }
                    return message;
                };

                /**
                 * Creates a plain object from a TypicalRequest message. Also converts values to other types if specified.
                 * @function toObject
                 * @memberof telepact.performance.v1.TypicalRequest
                 * @static
                 * @param {telepact.performance.v1.TypicalRequest} message TypicalRequest
                 * @param {$protobuf.IConversionOptions} [options] Conversion options
                 * @returns {Object.<string,*>} Plain object
                 */
                TypicalRequest.toObject = function toObject(message, options) {
                    if (!options)
                        options = {};
                    let object = {};
                    if (options.arrays || options.defaults)
                        object.items = [];
                    if (message.items && message.items.length) {
                        object.items = Array(message.items.length);
                        for (let j = 0; j < message.items.length; ++j)
                            object.items[j] = $root.telepact.performance.v1.TypicalItem.toObject(message.items[j], options);
                    }
                    return object;
                };

                /**
                 * Converts this TypicalRequest to JSON.
                 * @function toJSON
                 * @memberof telepact.performance.v1.TypicalRequest
                 * @instance
                 * @returns {Object.<string,*>} JSON object
                 */
                TypicalRequest.prototype.toJSON = function toJSON() {
                    return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
                };

                /**
                 * Gets the type url for TypicalRequest
                 * @function getTypeUrl
                 * @memberof telepact.performance.v1.TypicalRequest
                 * @static
                 * @param {string} [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
                 * @returns {string} The type url
                 */
                TypicalRequest.getTypeUrl = function getTypeUrl(prefix) {
                    if (prefix === undefined)
                        prefix = "type.googleapis.com";
                    return prefix + "/telepact.performance.v1.TypicalRequest";
                };

                return TypicalRequest;
            })();

            v1.TypicalResponse = (function() {

                /**
                 * Properties of a TypicalResponse.
                 * @memberof telepact.performance.v1
                 * @interface ITypicalResponse
                 * @property {Array.<telepact.performance.v1.ITypicalItem>|null} [items] TypicalResponse items
                 * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding
                 */

                /**
                 * Constructs a new TypicalResponse.
                 * @memberof telepact.performance.v1
                 * @classdesc Represents a TypicalResponse.
                 * @implements ITypicalResponse
                 * @constructor
                 * @param {telepact.performance.v1.ITypicalResponse=} [properties] Properties to set
                 * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding
                 */
                function TypicalResponse(properties) {
                    this.items = [];
                    if (properties)
                        for (let keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                            if (properties[keys[i]] != null && keys[i] !== "__proto__")
                                this[keys[i]] = properties[keys[i]];
                }

                /**
                 * TypicalResponse items.
                 * @member {Array.<telepact.performance.v1.ITypicalItem>} items
                 * @memberof telepact.performance.v1.TypicalResponse
                 * @instance
                 */
                TypicalResponse.prototype.items = $util.emptyArray;

                /**
                 * Creates a new TypicalResponse instance using the specified properties.
                 * @function create
                 * @memberof telepact.performance.v1.TypicalResponse
                 * @static
                 * @param {telepact.performance.v1.ITypicalResponse=} [properties] Properties to set
                 * @returns {telepact.performance.v1.TypicalResponse} TypicalResponse instance
                 */
                TypicalResponse.create = function create(properties) {
                    return new TypicalResponse(properties);
                };

                /**
                 * Encodes the specified TypicalResponse message. Does not implicitly {@link telepact.performance.v1.TypicalResponse.verify|verify} messages.
                 * @function encode
                 * @memberof telepact.performance.v1.TypicalResponse
                 * @static
                 * @param {telepact.performance.v1.ITypicalResponse} message TypicalResponse message or plain object to encode
                 * @param {$protobuf.Writer} [writer] Writer to encode to
                 * @returns {$protobuf.Writer} Writer
                 */
                TypicalResponse.encode = function encode(message, writer) {
                    if (!writer)
                        writer = $Writer.create();
                    if (message.items != null && message.items.length)
                        for (let i = 0; i < message.items.length; ++i)
                            $root.telepact.performance.v1.TypicalItem.encode(message.items[i], writer.uint32(/* id 1, wireType 2 =*/10).fork()).ldelim();
                    if (message.$unknowns != null && Object.hasOwnProperty.call(message, "$unknowns"))
                        for (let i = 0; i < message.$unknowns.length; ++i)
                            writer.raw(message.$unknowns[i]);
                    return writer;
                };

                /**
                 * Encodes the specified TypicalResponse message, length delimited. Does not implicitly {@link telepact.performance.v1.TypicalResponse.verify|verify} messages.
                 * @function encodeDelimited
                 * @memberof telepact.performance.v1.TypicalResponse
                 * @static
                 * @param {telepact.performance.v1.ITypicalResponse} message TypicalResponse message or plain object to encode
                 * @param {$protobuf.Writer} [writer] Writer to encode to
                 * @returns {$protobuf.Writer} Writer
                 */
                TypicalResponse.encodeDelimited = function encodeDelimited(message, writer) {
                    return this.encode(message, writer).ldelim();
                };

                /**
                 * Decodes a TypicalResponse message from the specified reader or buffer.
                 * @function decode
                 * @memberof telepact.performance.v1.TypicalResponse
                 * @static
                 * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
                 * @param {number} [length] Message length if known beforehand
                 * @returns {telepact.performance.v1.TypicalResponse} TypicalResponse
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                TypicalResponse.decode = function decode(reader, length, _end, _depth, _target) {
                    if (!(reader instanceof $Reader))
                        reader = $Reader.create(reader);
                    if (_depth === undefined)
                        _depth = 0;
                    if (_depth > $Reader.recursionLimit)
                        throw Error("max depth exceeded");
                    let end = length === undefined ? reader.len : reader.pos + length, message = _target || new $root.telepact.performance.v1.TypicalResponse();
                    while (reader.pos < end) {
                        let start = reader.pos;
                        let tag = reader.tag();
                        if (tag === _end) {
                            _end = undefined;
                            break;
                        }
                        let wireType = tag & 7;
                        switch (tag >>>= 3) {
                        case 1: {
                                if (wireType !== 2)
                                    break;
                                if (!(message.items && message.items.length))
                                    message.items = [];
                                message.items.push($root.telepact.performance.v1.TypicalItem.decode(reader, reader.uint32(), undefined, _depth + 1));
                                continue;
                            }
                        }
                        reader.skipType(wireType, _depth, tag);
                        $util.makeProp(message, "$unknowns", false);
                        (message.$unknowns || (message.$unknowns = [])).push(reader.raw(start, reader.pos));
                    }
                    if (_end !== undefined)
                        throw Error("missing end group");
                    return message;
                };

                /**
                 * Decodes a TypicalResponse message from the specified reader or buffer, length delimited.
                 * @function decodeDelimited
                 * @memberof telepact.performance.v1.TypicalResponse
                 * @static
                 * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
                 * @returns {telepact.performance.v1.TypicalResponse} TypicalResponse
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                TypicalResponse.decodeDelimited = function decodeDelimited(reader) {
                    if (!(reader instanceof $Reader))
                        reader = new $Reader(reader);
                    return this.decode(reader, reader.uint32());
                };

                /**
                 * Verifies a TypicalResponse message.
                 * @function verify
                 * @memberof telepact.performance.v1.TypicalResponse
                 * @static
                 * @param {Object.<string,*>} message Plain object to verify
                 * @returns {string|null} `null` if valid, otherwise the reason why it is not
                 */
                TypicalResponse.verify = function verify(message, _depth) {
                    if (typeof message !== "object" || message === null)
                        return "object expected";
                    if (_depth === undefined)
                        _depth = 0;
                    if (_depth > $util.recursionLimit)
                        return "max depth exceeded";
                    if (message.items != null && message.hasOwnProperty("items")) {
                        if (!Array.isArray(message.items))
                            return "items: array expected";
                        for (let i = 0; i < message.items.length; ++i) {
                            let error = $root.telepact.performance.v1.TypicalItem.verify(message.items[i], _depth + 1);
                            if (error)
                                return "items." + error;
                        }
                    }
                    return null;
                };

                /**
                 * Creates a TypicalResponse message from a plain object. Also converts values to their respective internal types.
                 * @function fromObject
                 * @memberof telepact.performance.v1.TypicalResponse
                 * @static
                 * @param {Object.<string,*>} object Plain object
                 * @returns {telepact.performance.v1.TypicalResponse} TypicalResponse
                 */
                TypicalResponse.fromObject = function fromObject(object, _depth) {
                    if (object instanceof $root.telepact.performance.v1.TypicalResponse)
                        return object;
                    if (_depth === undefined)
                        _depth = 0;
                    if (_depth > $util.recursionLimit)
                        throw Error("max depth exceeded");
                    let message = new $root.telepact.performance.v1.TypicalResponse();
                    if (object.items) {
                        if (!Array.isArray(object.items))
                            throw TypeError(".telepact.performance.v1.TypicalResponse.items: array expected");
                        message.items = Array(object.items.length);
                        for (let i = 0; i < object.items.length; ++i) {
                            if (typeof object.items[i] !== "object")
                                throw TypeError(".telepact.performance.v1.TypicalResponse.items: object expected");
                            message.items[i] = $root.telepact.performance.v1.TypicalItem.fromObject(object.items[i], _depth + 1);
                        }
                    }
                    return message;
                };

                /**
                 * Creates a plain object from a TypicalResponse message. Also converts values to other types if specified.
                 * @function toObject
                 * @memberof telepact.performance.v1.TypicalResponse
                 * @static
                 * @param {telepact.performance.v1.TypicalResponse} message TypicalResponse
                 * @param {$protobuf.IConversionOptions} [options] Conversion options
                 * @returns {Object.<string,*>} Plain object
                 */
                TypicalResponse.toObject = function toObject(message, options) {
                    if (!options)
                        options = {};
                    let object = {};
                    if (options.arrays || options.defaults)
                        object.items = [];
                    if (message.items && message.items.length) {
                        object.items = Array(message.items.length);
                        for (let j = 0; j < message.items.length; ++j)
                            object.items[j] = $root.telepact.performance.v1.TypicalItem.toObject(message.items[j], options);
                    }
                    return object;
                };

                /**
                 * Converts this TypicalResponse to JSON.
                 * @function toJSON
                 * @memberof telepact.performance.v1.TypicalResponse
                 * @instance
                 * @returns {Object.<string,*>} JSON object
                 */
                TypicalResponse.prototype.toJSON = function toJSON() {
                    return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
                };

                /**
                 * Gets the type url for TypicalResponse
                 * @function getTypeUrl
                 * @memberof telepact.performance.v1.TypicalResponse
                 * @static
                 * @param {string} [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
                 * @returns {string} The type url
                 */
                TypicalResponse.getTypeUrl = function getTypeUrl(prefix) {
                    if (prefix === undefined)
                        prefix = "type.googleapis.com";
                    return prefix + "/telepact.performance.v1.TypicalResponse";
                };

                return TypicalResponse;
            })();

            v1.StringsRequest = (function() {

                /**
                 * Properties of a StringsRequest.
                 * @memberof telepact.performance.v1
                 * @interface IStringsRequest
                 * @property {Array.<telepact.performance.v1.IStringItem>|null} [items] StringsRequest items
                 * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding
                 */

                /**
                 * Constructs a new StringsRequest.
                 * @memberof telepact.performance.v1
                 * @classdesc Represents a StringsRequest.
                 * @implements IStringsRequest
                 * @constructor
                 * @param {telepact.performance.v1.IStringsRequest=} [properties] Properties to set
                 * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding
                 */
                function StringsRequest(properties) {
                    this.items = [];
                    if (properties)
                        for (let keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                            if (properties[keys[i]] != null && keys[i] !== "__proto__")
                                this[keys[i]] = properties[keys[i]];
                }

                /**
                 * StringsRequest items.
                 * @member {Array.<telepact.performance.v1.IStringItem>} items
                 * @memberof telepact.performance.v1.StringsRequest
                 * @instance
                 */
                StringsRequest.prototype.items = $util.emptyArray;

                /**
                 * Creates a new StringsRequest instance using the specified properties.
                 * @function create
                 * @memberof telepact.performance.v1.StringsRequest
                 * @static
                 * @param {telepact.performance.v1.IStringsRequest=} [properties] Properties to set
                 * @returns {telepact.performance.v1.StringsRequest} StringsRequest instance
                 */
                StringsRequest.create = function create(properties) {
                    return new StringsRequest(properties);
                };

                /**
                 * Encodes the specified StringsRequest message. Does not implicitly {@link telepact.performance.v1.StringsRequest.verify|verify} messages.
                 * @function encode
                 * @memberof telepact.performance.v1.StringsRequest
                 * @static
                 * @param {telepact.performance.v1.IStringsRequest} message StringsRequest message or plain object to encode
                 * @param {$protobuf.Writer} [writer] Writer to encode to
                 * @returns {$protobuf.Writer} Writer
                 */
                StringsRequest.encode = function encode(message, writer) {
                    if (!writer)
                        writer = $Writer.create();
                    if (message.items != null && message.items.length)
                        for (let i = 0; i < message.items.length; ++i)
                            $root.telepact.performance.v1.StringItem.encode(message.items[i], writer.uint32(/* id 1, wireType 2 =*/10).fork()).ldelim();
                    if (message.$unknowns != null && Object.hasOwnProperty.call(message, "$unknowns"))
                        for (let i = 0; i < message.$unknowns.length; ++i)
                            writer.raw(message.$unknowns[i]);
                    return writer;
                };

                /**
                 * Encodes the specified StringsRequest message, length delimited. Does not implicitly {@link telepact.performance.v1.StringsRequest.verify|verify} messages.
                 * @function encodeDelimited
                 * @memberof telepact.performance.v1.StringsRequest
                 * @static
                 * @param {telepact.performance.v1.IStringsRequest} message StringsRequest message or plain object to encode
                 * @param {$protobuf.Writer} [writer] Writer to encode to
                 * @returns {$protobuf.Writer} Writer
                 */
                StringsRequest.encodeDelimited = function encodeDelimited(message, writer) {
                    return this.encode(message, writer).ldelim();
                };

                /**
                 * Decodes a StringsRequest message from the specified reader or buffer.
                 * @function decode
                 * @memberof telepact.performance.v1.StringsRequest
                 * @static
                 * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
                 * @param {number} [length] Message length if known beforehand
                 * @returns {telepact.performance.v1.StringsRequest} StringsRequest
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                StringsRequest.decode = function decode(reader, length, _end, _depth, _target) {
                    if (!(reader instanceof $Reader))
                        reader = $Reader.create(reader);
                    if (_depth === undefined)
                        _depth = 0;
                    if (_depth > $Reader.recursionLimit)
                        throw Error("max depth exceeded");
                    let end = length === undefined ? reader.len : reader.pos + length, message = _target || new $root.telepact.performance.v1.StringsRequest();
                    while (reader.pos < end) {
                        let start = reader.pos;
                        let tag = reader.tag();
                        if (tag === _end) {
                            _end = undefined;
                            break;
                        }
                        let wireType = tag & 7;
                        switch (tag >>>= 3) {
                        case 1: {
                                if (wireType !== 2)
                                    break;
                                if (!(message.items && message.items.length))
                                    message.items = [];
                                message.items.push($root.telepact.performance.v1.StringItem.decode(reader, reader.uint32(), undefined, _depth + 1));
                                continue;
                            }
                        }
                        reader.skipType(wireType, _depth, tag);
                        $util.makeProp(message, "$unknowns", false);
                        (message.$unknowns || (message.$unknowns = [])).push(reader.raw(start, reader.pos));
                    }
                    if (_end !== undefined)
                        throw Error("missing end group");
                    return message;
                };

                /**
                 * Decodes a StringsRequest message from the specified reader or buffer, length delimited.
                 * @function decodeDelimited
                 * @memberof telepact.performance.v1.StringsRequest
                 * @static
                 * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
                 * @returns {telepact.performance.v1.StringsRequest} StringsRequest
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                StringsRequest.decodeDelimited = function decodeDelimited(reader) {
                    if (!(reader instanceof $Reader))
                        reader = new $Reader(reader);
                    return this.decode(reader, reader.uint32());
                };

                /**
                 * Verifies a StringsRequest message.
                 * @function verify
                 * @memberof telepact.performance.v1.StringsRequest
                 * @static
                 * @param {Object.<string,*>} message Plain object to verify
                 * @returns {string|null} `null` if valid, otherwise the reason why it is not
                 */
                StringsRequest.verify = function verify(message, _depth) {
                    if (typeof message !== "object" || message === null)
                        return "object expected";
                    if (_depth === undefined)
                        _depth = 0;
                    if (_depth > $util.recursionLimit)
                        return "max depth exceeded";
                    if (message.items != null && message.hasOwnProperty("items")) {
                        if (!Array.isArray(message.items))
                            return "items: array expected";
                        for (let i = 0; i < message.items.length; ++i) {
                            let error = $root.telepact.performance.v1.StringItem.verify(message.items[i], _depth + 1);
                            if (error)
                                return "items." + error;
                        }
                    }
                    return null;
                };

                /**
                 * Creates a StringsRequest message from a plain object. Also converts values to their respective internal types.
                 * @function fromObject
                 * @memberof telepact.performance.v1.StringsRequest
                 * @static
                 * @param {Object.<string,*>} object Plain object
                 * @returns {telepact.performance.v1.StringsRequest} StringsRequest
                 */
                StringsRequest.fromObject = function fromObject(object, _depth) {
                    if (object instanceof $root.telepact.performance.v1.StringsRequest)
                        return object;
                    if (_depth === undefined)
                        _depth = 0;
                    if (_depth > $util.recursionLimit)
                        throw Error("max depth exceeded");
                    let message = new $root.telepact.performance.v1.StringsRequest();
                    if (object.items) {
                        if (!Array.isArray(object.items))
                            throw TypeError(".telepact.performance.v1.StringsRequest.items: array expected");
                        message.items = Array(object.items.length);
                        for (let i = 0; i < object.items.length; ++i) {
                            if (typeof object.items[i] !== "object")
                                throw TypeError(".telepact.performance.v1.StringsRequest.items: object expected");
                            message.items[i] = $root.telepact.performance.v1.StringItem.fromObject(object.items[i], _depth + 1);
                        }
                    }
                    return message;
                };

                /**
                 * Creates a plain object from a StringsRequest message. Also converts values to other types if specified.
                 * @function toObject
                 * @memberof telepact.performance.v1.StringsRequest
                 * @static
                 * @param {telepact.performance.v1.StringsRequest} message StringsRequest
                 * @param {$protobuf.IConversionOptions} [options] Conversion options
                 * @returns {Object.<string,*>} Plain object
                 */
                StringsRequest.toObject = function toObject(message, options) {
                    if (!options)
                        options = {};
                    let object = {};
                    if (options.arrays || options.defaults)
                        object.items = [];
                    if (message.items && message.items.length) {
                        object.items = Array(message.items.length);
                        for (let j = 0; j < message.items.length; ++j)
                            object.items[j] = $root.telepact.performance.v1.StringItem.toObject(message.items[j], options);
                    }
                    return object;
                };

                /**
                 * Converts this StringsRequest to JSON.
                 * @function toJSON
                 * @memberof telepact.performance.v1.StringsRequest
                 * @instance
                 * @returns {Object.<string,*>} JSON object
                 */
                StringsRequest.prototype.toJSON = function toJSON() {
                    return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
                };

                /**
                 * Gets the type url for StringsRequest
                 * @function getTypeUrl
                 * @memberof telepact.performance.v1.StringsRequest
                 * @static
                 * @param {string} [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
                 * @returns {string} The type url
                 */
                StringsRequest.getTypeUrl = function getTypeUrl(prefix) {
                    if (prefix === undefined)
                        prefix = "type.googleapis.com";
                    return prefix + "/telepact.performance.v1.StringsRequest";
                };

                return StringsRequest;
            })();

            v1.StringsResponse = (function() {

                /**
                 * Properties of a StringsResponse.
                 * @memberof telepact.performance.v1
                 * @interface IStringsResponse
                 * @property {Array.<telepact.performance.v1.IStringItem>|null} [items] StringsResponse items
                 * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding
                 */

                /**
                 * Constructs a new StringsResponse.
                 * @memberof telepact.performance.v1
                 * @classdesc Represents a StringsResponse.
                 * @implements IStringsResponse
                 * @constructor
                 * @param {telepact.performance.v1.IStringsResponse=} [properties] Properties to set
                 * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding
                 */
                function StringsResponse(properties) {
                    this.items = [];
                    if (properties)
                        for (let keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                            if (properties[keys[i]] != null && keys[i] !== "__proto__")
                                this[keys[i]] = properties[keys[i]];
                }

                /**
                 * StringsResponse items.
                 * @member {Array.<telepact.performance.v1.IStringItem>} items
                 * @memberof telepact.performance.v1.StringsResponse
                 * @instance
                 */
                StringsResponse.prototype.items = $util.emptyArray;

                /**
                 * Creates a new StringsResponse instance using the specified properties.
                 * @function create
                 * @memberof telepact.performance.v1.StringsResponse
                 * @static
                 * @param {telepact.performance.v1.IStringsResponse=} [properties] Properties to set
                 * @returns {telepact.performance.v1.StringsResponse} StringsResponse instance
                 */
                StringsResponse.create = function create(properties) {
                    return new StringsResponse(properties);
                };

                /**
                 * Encodes the specified StringsResponse message. Does not implicitly {@link telepact.performance.v1.StringsResponse.verify|verify} messages.
                 * @function encode
                 * @memberof telepact.performance.v1.StringsResponse
                 * @static
                 * @param {telepact.performance.v1.IStringsResponse} message StringsResponse message or plain object to encode
                 * @param {$protobuf.Writer} [writer] Writer to encode to
                 * @returns {$protobuf.Writer} Writer
                 */
                StringsResponse.encode = function encode(message, writer) {
                    if (!writer)
                        writer = $Writer.create();
                    if (message.items != null && message.items.length)
                        for (let i = 0; i < message.items.length; ++i)
                            $root.telepact.performance.v1.StringItem.encode(message.items[i], writer.uint32(/* id 1, wireType 2 =*/10).fork()).ldelim();
                    if (message.$unknowns != null && Object.hasOwnProperty.call(message, "$unknowns"))
                        for (let i = 0; i < message.$unknowns.length; ++i)
                            writer.raw(message.$unknowns[i]);
                    return writer;
                };

                /**
                 * Encodes the specified StringsResponse message, length delimited. Does not implicitly {@link telepact.performance.v1.StringsResponse.verify|verify} messages.
                 * @function encodeDelimited
                 * @memberof telepact.performance.v1.StringsResponse
                 * @static
                 * @param {telepact.performance.v1.IStringsResponse} message StringsResponse message or plain object to encode
                 * @param {$protobuf.Writer} [writer] Writer to encode to
                 * @returns {$protobuf.Writer} Writer
                 */
                StringsResponse.encodeDelimited = function encodeDelimited(message, writer) {
                    return this.encode(message, writer).ldelim();
                };

                /**
                 * Decodes a StringsResponse message from the specified reader or buffer.
                 * @function decode
                 * @memberof telepact.performance.v1.StringsResponse
                 * @static
                 * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
                 * @param {number} [length] Message length if known beforehand
                 * @returns {telepact.performance.v1.StringsResponse} StringsResponse
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                StringsResponse.decode = function decode(reader, length, _end, _depth, _target) {
                    if (!(reader instanceof $Reader))
                        reader = $Reader.create(reader);
                    if (_depth === undefined)
                        _depth = 0;
                    if (_depth > $Reader.recursionLimit)
                        throw Error("max depth exceeded");
                    let end = length === undefined ? reader.len : reader.pos + length, message = _target || new $root.telepact.performance.v1.StringsResponse();
                    while (reader.pos < end) {
                        let start = reader.pos;
                        let tag = reader.tag();
                        if (tag === _end) {
                            _end = undefined;
                            break;
                        }
                        let wireType = tag & 7;
                        switch (tag >>>= 3) {
                        case 1: {
                                if (wireType !== 2)
                                    break;
                                if (!(message.items && message.items.length))
                                    message.items = [];
                                message.items.push($root.telepact.performance.v1.StringItem.decode(reader, reader.uint32(), undefined, _depth + 1));
                                continue;
                            }
                        }
                        reader.skipType(wireType, _depth, tag);
                        $util.makeProp(message, "$unknowns", false);
                        (message.$unknowns || (message.$unknowns = [])).push(reader.raw(start, reader.pos));
                    }
                    if (_end !== undefined)
                        throw Error("missing end group");
                    return message;
                };

                /**
                 * Decodes a StringsResponse message from the specified reader or buffer, length delimited.
                 * @function decodeDelimited
                 * @memberof telepact.performance.v1.StringsResponse
                 * @static
                 * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
                 * @returns {telepact.performance.v1.StringsResponse} StringsResponse
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                StringsResponse.decodeDelimited = function decodeDelimited(reader) {
                    if (!(reader instanceof $Reader))
                        reader = new $Reader(reader);
                    return this.decode(reader, reader.uint32());
                };

                /**
                 * Verifies a StringsResponse message.
                 * @function verify
                 * @memberof telepact.performance.v1.StringsResponse
                 * @static
                 * @param {Object.<string,*>} message Plain object to verify
                 * @returns {string|null} `null` if valid, otherwise the reason why it is not
                 */
                StringsResponse.verify = function verify(message, _depth) {
                    if (typeof message !== "object" || message === null)
                        return "object expected";
                    if (_depth === undefined)
                        _depth = 0;
                    if (_depth > $util.recursionLimit)
                        return "max depth exceeded";
                    if (message.items != null && message.hasOwnProperty("items")) {
                        if (!Array.isArray(message.items))
                            return "items: array expected";
                        for (let i = 0; i < message.items.length; ++i) {
                            let error = $root.telepact.performance.v1.StringItem.verify(message.items[i], _depth + 1);
                            if (error)
                                return "items." + error;
                        }
                    }
                    return null;
                };

                /**
                 * Creates a StringsResponse message from a plain object. Also converts values to their respective internal types.
                 * @function fromObject
                 * @memberof telepact.performance.v1.StringsResponse
                 * @static
                 * @param {Object.<string,*>} object Plain object
                 * @returns {telepact.performance.v1.StringsResponse} StringsResponse
                 */
                StringsResponse.fromObject = function fromObject(object, _depth) {
                    if (object instanceof $root.telepact.performance.v1.StringsResponse)
                        return object;
                    if (_depth === undefined)
                        _depth = 0;
                    if (_depth > $util.recursionLimit)
                        throw Error("max depth exceeded");
                    let message = new $root.telepact.performance.v1.StringsResponse();
                    if (object.items) {
                        if (!Array.isArray(object.items))
                            throw TypeError(".telepact.performance.v1.StringsResponse.items: array expected");
                        message.items = Array(object.items.length);
                        for (let i = 0; i < object.items.length; ++i) {
                            if (typeof object.items[i] !== "object")
                                throw TypeError(".telepact.performance.v1.StringsResponse.items: object expected");
                            message.items[i] = $root.telepact.performance.v1.StringItem.fromObject(object.items[i], _depth + 1);
                        }
                    }
                    return message;
                };

                /**
                 * Creates a plain object from a StringsResponse message. Also converts values to other types if specified.
                 * @function toObject
                 * @memberof telepact.performance.v1.StringsResponse
                 * @static
                 * @param {telepact.performance.v1.StringsResponse} message StringsResponse
                 * @param {$protobuf.IConversionOptions} [options] Conversion options
                 * @returns {Object.<string,*>} Plain object
                 */
                StringsResponse.toObject = function toObject(message, options) {
                    if (!options)
                        options = {};
                    let object = {};
                    if (options.arrays || options.defaults)
                        object.items = [];
                    if (message.items && message.items.length) {
                        object.items = Array(message.items.length);
                        for (let j = 0; j < message.items.length; ++j)
                            object.items[j] = $root.telepact.performance.v1.StringItem.toObject(message.items[j], options);
                    }
                    return object;
                };

                /**
                 * Converts this StringsResponse to JSON.
                 * @function toJSON
                 * @memberof telepact.performance.v1.StringsResponse
                 * @instance
                 * @returns {Object.<string,*>} JSON object
                 */
                StringsResponse.prototype.toJSON = function toJSON() {
                    return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
                };

                /**
                 * Gets the type url for StringsResponse
                 * @function getTypeUrl
                 * @memberof telepact.performance.v1.StringsResponse
                 * @static
                 * @param {string} [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
                 * @returns {string} The type url
                 */
                StringsResponse.getTypeUrl = function getTypeUrl(prefix) {
                    if (prefix === undefined)
                        prefix = "type.googleapis.com";
                    return prefix + "/telepact.performance.v1.StringsResponse";
                };

                return StringsResponse;
            })();

            v1.NumbersRequest = (function() {

                /**
                 * Properties of a NumbersRequest.
                 * @memberof telepact.performance.v1
                 * @interface INumbersRequest
                 * @property {Array.<telepact.performance.v1.INumberItem>|null} [items] NumbersRequest items
                 * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding
                 */

                /**
                 * Constructs a new NumbersRequest.
                 * @memberof telepact.performance.v1
                 * @classdesc Represents a NumbersRequest.
                 * @implements INumbersRequest
                 * @constructor
                 * @param {telepact.performance.v1.INumbersRequest=} [properties] Properties to set
                 * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding
                 */
                function NumbersRequest(properties) {
                    this.items = [];
                    if (properties)
                        for (let keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                            if (properties[keys[i]] != null && keys[i] !== "__proto__")
                                this[keys[i]] = properties[keys[i]];
                }

                /**
                 * NumbersRequest items.
                 * @member {Array.<telepact.performance.v1.INumberItem>} items
                 * @memberof telepact.performance.v1.NumbersRequest
                 * @instance
                 */
                NumbersRequest.prototype.items = $util.emptyArray;

                /**
                 * Creates a new NumbersRequest instance using the specified properties.
                 * @function create
                 * @memberof telepact.performance.v1.NumbersRequest
                 * @static
                 * @param {telepact.performance.v1.INumbersRequest=} [properties] Properties to set
                 * @returns {telepact.performance.v1.NumbersRequest} NumbersRequest instance
                 */
                NumbersRequest.create = function create(properties) {
                    return new NumbersRequest(properties);
                };

                /**
                 * Encodes the specified NumbersRequest message. Does not implicitly {@link telepact.performance.v1.NumbersRequest.verify|verify} messages.
                 * @function encode
                 * @memberof telepact.performance.v1.NumbersRequest
                 * @static
                 * @param {telepact.performance.v1.INumbersRequest} message NumbersRequest message or plain object to encode
                 * @param {$protobuf.Writer} [writer] Writer to encode to
                 * @returns {$protobuf.Writer} Writer
                 */
                NumbersRequest.encode = function encode(message, writer) {
                    if (!writer)
                        writer = $Writer.create();
                    if (message.items != null && message.items.length)
                        for (let i = 0; i < message.items.length; ++i)
                            $root.telepact.performance.v1.NumberItem.encode(message.items[i], writer.uint32(/* id 1, wireType 2 =*/10).fork()).ldelim();
                    if (message.$unknowns != null && Object.hasOwnProperty.call(message, "$unknowns"))
                        for (let i = 0; i < message.$unknowns.length; ++i)
                            writer.raw(message.$unknowns[i]);
                    return writer;
                };

                /**
                 * Encodes the specified NumbersRequest message, length delimited. Does not implicitly {@link telepact.performance.v1.NumbersRequest.verify|verify} messages.
                 * @function encodeDelimited
                 * @memberof telepact.performance.v1.NumbersRequest
                 * @static
                 * @param {telepact.performance.v1.INumbersRequest} message NumbersRequest message or plain object to encode
                 * @param {$protobuf.Writer} [writer] Writer to encode to
                 * @returns {$protobuf.Writer} Writer
                 */
                NumbersRequest.encodeDelimited = function encodeDelimited(message, writer) {
                    return this.encode(message, writer).ldelim();
                };

                /**
                 * Decodes a NumbersRequest message from the specified reader or buffer.
                 * @function decode
                 * @memberof telepact.performance.v1.NumbersRequest
                 * @static
                 * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
                 * @param {number} [length] Message length if known beforehand
                 * @returns {telepact.performance.v1.NumbersRequest} NumbersRequest
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                NumbersRequest.decode = function decode(reader, length, _end, _depth, _target) {
                    if (!(reader instanceof $Reader))
                        reader = $Reader.create(reader);
                    if (_depth === undefined)
                        _depth = 0;
                    if (_depth > $Reader.recursionLimit)
                        throw Error("max depth exceeded");
                    let end = length === undefined ? reader.len : reader.pos + length, message = _target || new $root.telepact.performance.v1.NumbersRequest();
                    while (reader.pos < end) {
                        let start = reader.pos;
                        let tag = reader.tag();
                        if (tag === _end) {
                            _end = undefined;
                            break;
                        }
                        let wireType = tag & 7;
                        switch (tag >>>= 3) {
                        case 1: {
                                if (wireType !== 2)
                                    break;
                                if (!(message.items && message.items.length))
                                    message.items = [];
                                message.items.push($root.telepact.performance.v1.NumberItem.decode(reader, reader.uint32(), undefined, _depth + 1));
                                continue;
                            }
                        }
                        reader.skipType(wireType, _depth, tag);
                        $util.makeProp(message, "$unknowns", false);
                        (message.$unknowns || (message.$unknowns = [])).push(reader.raw(start, reader.pos));
                    }
                    if (_end !== undefined)
                        throw Error("missing end group");
                    return message;
                };

                /**
                 * Decodes a NumbersRequest message from the specified reader or buffer, length delimited.
                 * @function decodeDelimited
                 * @memberof telepact.performance.v1.NumbersRequest
                 * @static
                 * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
                 * @returns {telepact.performance.v1.NumbersRequest} NumbersRequest
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                NumbersRequest.decodeDelimited = function decodeDelimited(reader) {
                    if (!(reader instanceof $Reader))
                        reader = new $Reader(reader);
                    return this.decode(reader, reader.uint32());
                };

                /**
                 * Verifies a NumbersRequest message.
                 * @function verify
                 * @memberof telepact.performance.v1.NumbersRequest
                 * @static
                 * @param {Object.<string,*>} message Plain object to verify
                 * @returns {string|null} `null` if valid, otherwise the reason why it is not
                 */
                NumbersRequest.verify = function verify(message, _depth) {
                    if (typeof message !== "object" || message === null)
                        return "object expected";
                    if (_depth === undefined)
                        _depth = 0;
                    if (_depth > $util.recursionLimit)
                        return "max depth exceeded";
                    if (message.items != null && message.hasOwnProperty("items")) {
                        if (!Array.isArray(message.items))
                            return "items: array expected";
                        for (let i = 0; i < message.items.length; ++i) {
                            let error = $root.telepact.performance.v1.NumberItem.verify(message.items[i], _depth + 1);
                            if (error)
                                return "items." + error;
                        }
                    }
                    return null;
                };

                /**
                 * Creates a NumbersRequest message from a plain object. Also converts values to their respective internal types.
                 * @function fromObject
                 * @memberof telepact.performance.v1.NumbersRequest
                 * @static
                 * @param {Object.<string,*>} object Plain object
                 * @returns {telepact.performance.v1.NumbersRequest} NumbersRequest
                 */
                NumbersRequest.fromObject = function fromObject(object, _depth) {
                    if (object instanceof $root.telepact.performance.v1.NumbersRequest)
                        return object;
                    if (_depth === undefined)
                        _depth = 0;
                    if (_depth > $util.recursionLimit)
                        throw Error("max depth exceeded");
                    let message = new $root.telepact.performance.v1.NumbersRequest();
                    if (object.items) {
                        if (!Array.isArray(object.items))
                            throw TypeError(".telepact.performance.v1.NumbersRequest.items: array expected");
                        message.items = Array(object.items.length);
                        for (let i = 0; i < object.items.length; ++i) {
                            if (typeof object.items[i] !== "object")
                                throw TypeError(".telepact.performance.v1.NumbersRequest.items: object expected");
                            message.items[i] = $root.telepact.performance.v1.NumberItem.fromObject(object.items[i], _depth + 1);
                        }
                    }
                    return message;
                };

                /**
                 * Creates a plain object from a NumbersRequest message. Also converts values to other types if specified.
                 * @function toObject
                 * @memberof telepact.performance.v1.NumbersRequest
                 * @static
                 * @param {telepact.performance.v1.NumbersRequest} message NumbersRequest
                 * @param {$protobuf.IConversionOptions} [options] Conversion options
                 * @returns {Object.<string,*>} Plain object
                 */
                NumbersRequest.toObject = function toObject(message, options) {
                    if (!options)
                        options = {};
                    let object = {};
                    if (options.arrays || options.defaults)
                        object.items = [];
                    if (message.items && message.items.length) {
                        object.items = Array(message.items.length);
                        for (let j = 0; j < message.items.length; ++j)
                            object.items[j] = $root.telepact.performance.v1.NumberItem.toObject(message.items[j], options);
                    }
                    return object;
                };

                /**
                 * Converts this NumbersRequest to JSON.
                 * @function toJSON
                 * @memberof telepact.performance.v1.NumbersRequest
                 * @instance
                 * @returns {Object.<string,*>} JSON object
                 */
                NumbersRequest.prototype.toJSON = function toJSON() {
                    return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
                };

                /**
                 * Gets the type url for NumbersRequest
                 * @function getTypeUrl
                 * @memberof telepact.performance.v1.NumbersRequest
                 * @static
                 * @param {string} [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
                 * @returns {string} The type url
                 */
                NumbersRequest.getTypeUrl = function getTypeUrl(prefix) {
                    if (prefix === undefined)
                        prefix = "type.googleapis.com";
                    return prefix + "/telepact.performance.v1.NumbersRequest";
                };

                return NumbersRequest;
            })();

            v1.NumbersResponse = (function() {

                /**
                 * Properties of a NumbersResponse.
                 * @memberof telepact.performance.v1
                 * @interface INumbersResponse
                 * @property {Array.<telepact.performance.v1.INumberItem>|null} [items] NumbersResponse items
                 * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding
                 */

                /**
                 * Constructs a new NumbersResponse.
                 * @memberof telepact.performance.v1
                 * @classdesc Represents a NumbersResponse.
                 * @implements INumbersResponse
                 * @constructor
                 * @param {telepact.performance.v1.INumbersResponse=} [properties] Properties to set
                 * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding
                 */
                function NumbersResponse(properties) {
                    this.items = [];
                    if (properties)
                        for (let keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                            if (properties[keys[i]] != null && keys[i] !== "__proto__")
                                this[keys[i]] = properties[keys[i]];
                }

                /**
                 * NumbersResponse items.
                 * @member {Array.<telepact.performance.v1.INumberItem>} items
                 * @memberof telepact.performance.v1.NumbersResponse
                 * @instance
                 */
                NumbersResponse.prototype.items = $util.emptyArray;

                /**
                 * Creates a new NumbersResponse instance using the specified properties.
                 * @function create
                 * @memberof telepact.performance.v1.NumbersResponse
                 * @static
                 * @param {telepact.performance.v1.INumbersResponse=} [properties] Properties to set
                 * @returns {telepact.performance.v1.NumbersResponse} NumbersResponse instance
                 */
                NumbersResponse.create = function create(properties) {
                    return new NumbersResponse(properties);
                };

                /**
                 * Encodes the specified NumbersResponse message. Does not implicitly {@link telepact.performance.v1.NumbersResponse.verify|verify} messages.
                 * @function encode
                 * @memberof telepact.performance.v1.NumbersResponse
                 * @static
                 * @param {telepact.performance.v1.INumbersResponse} message NumbersResponse message or plain object to encode
                 * @param {$protobuf.Writer} [writer] Writer to encode to
                 * @returns {$protobuf.Writer} Writer
                 */
                NumbersResponse.encode = function encode(message, writer) {
                    if (!writer)
                        writer = $Writer.create();
                    if (message.items != null && message.items.length)
                        for (let i = 0; i < message.items.length; ++i)
                            $root.telepact.performance.v1.NumberItem.encode(message.items[i], writer.uint32(/* id 1, wireType 2 =*/10).fork()).ldelim();
                    if (message.$unknowns != null && Object.hasOwnProperty.call(message, "$unknowns"))
                        for (let i = 0; i < message.$unknowns.length; ++i)
                            writer.raw(message.$unknowns[i]);
                    return writer;
                };

                /**
                 * Encodes the specified NumbersResponse message, length delimited. Does not implicitly {@link telepact.performance.v1.NumbersResponse.verify|verify} messages.
                 * @function encodeDelimited
                 * @memberof telepact.performance.v1.NumbersResponse
                 * @static
                 * @param {telepact.performance.v1.INumbersResponse} message NumbersResponse message or plain object to encode
                 * @param {$protobuf.Writer} [writer] Writer to encode to
                 * @returns {$protobuf.Writer} Writer
                 */
                NumbersResponse.encodeDelimited = function encodeDelimited(message, writer) {
                    return this.encode(message, writer).ldelim();
                };

                /**
                 * Decodes a NumbersResponse message from the specified reader or buffer.
                 * @function decode
                 * @memberof telepact.performance.v1.NumbersResponse
                 * @static
                 * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
                 * @param {number} [length] Message length if known beforehand
                 * @returns {telepact.performance.v1.NumbersResponse} NumbersResponse
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                NumbersResponse.decode = function decode(reader, length, _end, _depth, _target) {
                    if (!(reader instanceof $Reader))
                        reader = $Reader.create(reader);
                    if (_depth === undefined)
                        _depth = 0;
                    if (_depth > $Reader.recursionLimit)
                        throw Error("max depth exceeded");
                    let end = length === undefined ? reader.len : reader.pos + length, message = _target || new $root.telepact.performance.v1.NumbersResponse();
                    while (reader.pos < end) {
                        let start = reader.pos;
                        let tag = reader.tag();
                        if (tag === _end) {
                            _end = undefined;
                            break;
                        }
                        let wireType = tag & 7;
                        switch (tag >>>= 3) {
                        case 1: {
                                if (wireType !== 2)
                                    break;
                                if (!(message.items && message.items.length))
                                    message.items = [];
                                message.items.push($root.telepact.performance.v1.NumberItem.decode(reader, reader.uint32(), undefined, _depth + 1));
                                continue;
                            }
                        }
                        reader.skipType(wireType, _depth, tag);
                        $util.makeProp(message, "$unknowns", false);
                        (message.$unknowns || (message.$unknowns = [])).push(reader.raw(start, reader.pos));
                    }
                    if (_end !== undefined)
                        throw Error("missing end group");
                    return message;
                };

                /**
                 * Decodes a NumbersResponse message from the specified reader or buffer, length delimited.
                 * @function decodeDelimited
                 * @memberof telepact.performance.v1.NumbersResponse
                 * @static
                 * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
                 * @returns {telepact.performance.v1.NumbersResponse} NumbersResponse
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                NumbersResponse.decodeDelimited = function decodeDelimited(reader) {
                    if (!(reader instanceof $Reader))
                        reader = new $Reader(reader);
                    return this.decode(reader, reader.uint32());
                };

                /**
                 * Verifies a NumbersResponse message.
                 * @function verify
                 * @memberof telepact.performance.v1.NumbersResponse
                 * @static
                 * @param {Object.<string,*>} message Plain object to verify
                 * @returns {string|null} `null` if valid, otherwise the reason why it is not
                 */
                NumbersResponse.verify = function verify(message, _depth) {
                    if (typeof message !== "object" || message === null)
                        return "object expected";
                    if (_depth === undefined)
                        _depth = 0;
                    if (_depth > $util.recursionLimit)
                        return "max depth exceeded";
                    if (message.items != null && message.hasOwnProperty("items")) {
                        if (!Array.isArray(message.items))
                            return "items: array expected";
                        for (let i = 0; i < message.items.length; ++i) {
                            let error = $root.telepact.performance.v1.NumberItem.verify(message.items[i], _depth + 1);
                            if (error)
                                return "items." + error;
                        }
                    }
                    return null;
                };

                /**
                 * Creates a NumbersResponse message from a plain object. Also converts values to their respective internal types.
                 * @function fromObject
                 * @memberof telepact.performance.v1.NumbersResponse
                 * @static
                 * @param {Object.<string,*>} object Plain object
                 * @returns {telepact.performance.v1.NumbersResponse} NumbersResponse
                 */
                NumbersResponse.fromObject = function fromObject(object, _depth) {
                    if (object instanceof $root.telepact.performance.v1.NumbersResponse)
                        return object;
                    if (_depth === undefined)
                        _depth = 0;
                    if (_depth > $util.recursionLimit)
                        throw Error("max depth exceeded");
                    let message = new $root.telepact.performance.v1.NumbersResponse();
                    if (object.items) {
                        if (!Array.isArray(object.items))
                            throw TypeError(".telepact.performance.v1.NumbersResponse.items: array expected");
                        message.items = Array(object.items.length);
                        for (let i = 0; i < object.items.length; ++i) {
                            if (typeof object.items[i] !== "object")
                                throw TypeError(".telepact.performance.v1.NumbersResponse.items: object expected");
                            message.items[i] = $root.telepact.performance.v1.NumberItem.fromObject(object.items[i], _depth + 1);
                        }
                    }
                    return message;
                };

                /**
                 * Creates a plain object from a NumbersResponse message. Also converts values to other types if specified.
                 * @function toObject
                 * @memberof telepact.performance.v1.NumbersResponse
                 * @static
                 * @param {telepact.performance.v1.NumbersResponse} message NumbersResponse
                 * @param {$protobuf.IConversionOptions} [options] Conversion options
                 * @returns {Object.<string,*>} Plain object
                 */
                NumbersResponse.toObject = function toObject(message, options) {
                    if (!options)
                        options = {};
                    let object = {};
                    if (options.arrays || options.defaults)
                        object.items = [];
                    if (message.items && message.items.length) {
                        object.items = Array(message.items.length);
                        for (let j = 0; j < message.items.length; ++j)
                            object.items[j] = $root.telepact.performance.v1.NumberItem.toObject(message.items[j], options);
                    }
                    return object;
                };

                /**
                 * Converts this NumbersResponse to JSON.
                 * @function toJSON
                 * @memberof telepact.performance.v1.NumbersResponse
                 * @instance
                 * @returns {Object.<string,*>} JSON object
                 */
                NumbersResponse.prototype.toJSON = function toJSON() {
                    return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
                };

                /**
                 * Gets the type url for NumbersResponse
                 * @function getTypeUrl
                 * @memberof telepact.performance.v1.NumbersResponse
                 * @static
                 * @param {string} [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
                 * @returns {string} The type url
                 */
                NumbersResponse.getTypeUrl = function getTypeUrl(prefix) {
                    if (prefix === undefined)
                        prefix = "type.googleapis.com";
                    return prefix + "/telepact.performance.v1.NumbersResponse";
                };

                return NumbersResponse;
            })();

            v1.PerformanceService = (function() {

                /**
                 * Constructs a new PerformanceService service.
                 * @memberof telepact.performance.v1
                 * @classdesc Represents a PerformanceService
                 * @extends $protobuf.rpc.Service
                 * @constructor
                 * @param {$protobuf.RPCImpl} rpcImpl RPC implementation
                 * @param {boolean} [requestDelimited=false] Whether requests are length-delimited
                 * @param {boolean} [responseDelimited=false] Whether responses are length-delimited
                 */
                function PerformanceService(rpcImpl, requestDelimited, responseDelimited) {
                    $protobuf.rpc.Service.call(this, rpcImpl, requestDelimited, responseDelimited);
                }

                (PerformanceService.prototype = Object.create($protobuf.rpc.Service.prototype)).constructor = PerformanceService;

                /**
                 * Creates new PerformanceService service using the specified rpc implementation.
                 * @function create
                 * @memberof telepact.performance.v1.PerformanceService
                 * @static
                 * @param {$protobuf.RPCImpl} rpcImpl RPC implementation
                 * @param {boolean} [requestDelimited=false] Whether requests are length-delimited
                 * @param {boolean} [responseDelimited=false] Whether responses are length-delimited
                 * @returns {PerformanceService} RPC service. Useful where requests and/or responses are streamed.
                 */
                PerformanceService.create = function create(rpcImpl, requestDelimited, responseDelimited) {
                    return new this(rpcImpl, requestDelimited, responseDelimited);
                };

                /**
                 * Callback as used by {@link telepact.performance.v1.PerformanceService#roundTripTypical}.
                 * @memberof telepact.performance.v1.PerformanceService
                 * @typedef RoundTripTypicalCallback
                 * @type {function}
                 * @param {Error|null} error Error, if any
                 * @param {telepact.performance.v1.TypicalResponse} [response] TypicalResponse
                 */

                /**
                 * Calls RoundTripTypical.
                 * @function roundTripTypical
                 * @memberof telepact.performance.v1.PerformanceService
                 * @instance
                 * @param {telepact.performance.v1.ITypicalRequest} request TypicalRequest message or plain object
                 * @param {telepact.performance.v1.PerformanceService.RoundTripTypicalCallback} callback Node-style callback called with the error, if any, and TypicalResponse
                 * @returns {undefined}
                 * @variation 1
                 */
                Object.defineProperty(PerformanceService.prototype.roundTripTypical = function roundTripTypical(request, callback) {
                    return this.rpcCall(roundTripTypical, $root.telepact.performance.v1.TypicalRequest, $root.telepact.performance.v1.TypicalResponse, request, callback);
                }, "name", { value: "RoundTripTypical" });

                /**
                 * Calls RoundTripTypical.
                 * @function roundTripTypical
                 * @memberof telepact.performance.v1.PerformanceService
                 * @instance
                 * @param {telepact.performance.v1.ITypicalRequest} request TypicalRequest message or plain object
                 * @returns {Promise<telepact.performance.v1.TypicalResponse>} Promise
                 * @variation 2
                 */

                /**
                 * Callback as used by {@link telepact.performance.v1.PerformanceService#roundTripStrings}.
                 * @memberof telepact.performance.v1.PerformanceService
                 * @typedef RoundTripStringsCallback
                 * @type {function}
                 * @param {Error|null} error Error, if any
                 * @param {telepact.performance.v1.StringsResponse} [response] StringsResponse
                 */

                /**
                 * Calls RoundTripStrings.
                 * @function roundTripStrings
                 * @memberof telepact.performance.v1.PerformanceService
                 * @instance
                 * @param {telepact.performance.v1.IStringsRequest} request StringsRequest message or plain object
                 * @param {telepact.performance.v1.PerformanceService.RoundTripStringsCallback} callback Node-style callback called with the error, if any, and StringsResponse
                 * @returns {undefined}
                 * @variation 1
                 */
                Object.defineProperty(PerformanceService.prototype.roundTripStrings = function roundTripStrings(request, callback) {
                    return this.rpcCall(roundTripStrings, $root.telepact.performance.v1.StringsRequest, $root.telepact.performance.v1.StringsResponse, request, callback);
                }, "name", { value: "RoundTripStrings" });

                /**
                 * Calls RoundTripStrings.
                 * @function roundTripStrings
                 * @memberof telepact.performance.v1.PerformanceService
                 * @instance
                 * @param {telepact.performance.v1.IStringsRequest} request StringsRequest message or plain object
                 * @returns {Promise<telepact.performance.v1.StringsResponse>} Promise
                 * @variation 2
                 */

                /**
                 * Callback as used by {@link telepact.performance.v1.PerformanceService#roundTripNumbers}.
                 * @memberof telepact.performance.v1.PerformanceService
                 * @typedef RoundTripNumbersCallback
                 * @type {function}
                 * @param {Error|null} error Error, if any
                 * @param {telepact.performance.v1.NumbersResponse} [response] NumbersResponse
                 */

                /**
                 * Calls RoundTripNumbers.
                 * @function roundTripNumbers
                 * @memberof telepact.performance.v1.PerformanceService
                 * @instance
                 * @param {telepact.performance.v1.INumbersRequest} request NumbersRequest message or plain object
                 * @param {telepact.performance.v1.PerformanceService.RoundTripNumbersCallback} callback Node-style callback called with the error, if any, and NumbersResponse
                 * @returns {undefined}
                 * @variation 1
                 */
                Object.defineProperty(PerformanceService.prototype.roundTripNumbers = function roundTripNumbers(request, callback) {
                    return this.rpcCall(roundTripNumbers, $root.telepact.performance.v1.NumbersRequest, $root.telepact.performance.v1.NumbersResponse, request, callback);
                }, "name", { value: "RoundTripNumbers" });

                /**
                 * Calls RoundTripNumbers.
                 * @function roundTripNumbers
                 * @memberof telepact.performance.v1.PerformanceService
                 * @instance
                 * @param {telepact.performance.v1.INumbersRequest} request NumbersRequest message or plain object
                 * @returns {Promise<telepact.performance.v1.NumbersResponse>} Promise
                 * @variation 2
                 */

                return PerformanceService;
            })();

            return v1;
        })();

        return performance;
    })();

    return telepact;
})();

export {
  $root as default
};
