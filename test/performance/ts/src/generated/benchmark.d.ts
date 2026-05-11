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

import * as $protobuf from "protobufjs";
import Long = require("long");
/** Namespace telepact. */
export namespace telepact {

    /** Namespace performance. */
    namespace performance {

        /** Namespace v1. */
        namespace v1 {

            /** Properties of a TypicalItem. */
            interface ITypicalItem {

                /** TypicalItem accountId */
                accountId?: (number|Long|null);

                /** TypicalItem customerName */
                customerName?: (string|null);

                /** TypicalItem region */
                region?: (string|null);

                /** TypicalItem unitPrice */
                unitPrice?: (number|null);

                /** TypicalItem quantity */
                quantity?: (number|Long|null);

                /** Unknown fields preserved while decoding */
                $unknowns?: Uint8Array[];
            }

            /** Represents a TypicalItem. */
            class TypicalItem implements ITypicalItem {

                /**
                 * Constructs a new TypicalItem.
                 * @param [properties] Properties to set
                 */
                constructor(properties?: telepact.performance.v1.ITypicalItem);

                /** Unknown fields preserved while decoding */
                public $unknowns?: Uint8Array[];

                /** TypicalItem accountId. */
                public accountId: (number|Long);

                /** TypicalItem customerName. */
                public customerName: string;

                /** TypicalItem region. */
                public region: string;

                /** TypicalItem unitPrice. */
                public unitPrice: number;

                /** TypicalItem quantity. */
                public quantity: (number|Long);

                /**
                 * Creates a new TypicalItem instance using the specified properties.
                 * @param [properties] Properties to set
                 * @returns TypicalItem instance
                 */
                public static create(properties?: telepact.performance.v1.ITypicalItem): telepact.performance.v1.TypicalItem;

                /**
                 * Encodes the specified TypicalItem message. Does not implicitly {@link telepact.performance.v1.TypicalItem.verify|verify} messages.
                 * @param message TypicalItem message or plain object to encode
                 * @param [writer] Writer to encode to
                 * @returns Writer
                 */
                public static encode(message: telepact.performance.v1.ITypicalItem, writer?: $protobuf.Writer): $protobuf.Writer;

                /**
                 * Encodes the specified TypicalItem message, length delimited. Does not implicitly {@link telepact.performance.v1.TypicalItem.verify|verify} messages.
                 * @param message TypicalItem message or plain object to encode
                 * @param [writer] Writer to encode to
                 * @returns Writer
                 */
                public static encodeDelimited(message: telepact.performance.v1.ITypicalItem, writer?: $protobuf.Writer): $protobuf.Writer;

                /**
                 * Decodes a TypicalItem message from the specified reader or buffer.
                 * @param reader Reader or buffer to decode from
                 * @param [length] Message length if known beforehand
                 * @returns TypicalItem
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): telepact.performance.v1.TypicalItem;

                /**
                 * Decodes a TypicalItem message from the specified reader or buffer, length delimited.
                 * @param reader Reader or buffer to decode from
                 * @returns TypicalItem
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): telepact.performance.v1.TypicalItem;

                /**
                 * Verifies a TypicalItem message.
                 * @param message Plain object to verify
                 * @returns `null` if valid, otherwise the reason why it is not
                 */
                public static verify(message: { [k: string]: any }): (string|null);

                /**
                 * Creates a TypicalItem message from a plain object. Also converts values to their respective internal types.
                 * @param object Plain object
                 * @returns TypicalItem
                 */
                public static fromObject(object: { [k: string]: any }): telepact.performance.v1.TypicalItem;

                /**
                 * Creates a plain object from a TypicalItem message. Also converts values to other types if specified.
                 * @param message TypicalItem
                 * @param [options] Conversion options
                 * @returns Plain object
                 */
                public static toObject(message: telepact.performance.v1.TypicalItem, options?: $protobuf.IConversionOptions): { [k: string]: any };

                /**
                 * Converts this TypicalItem to JSON.
                 * @returns JSON object
                 */
                public toJSON(): { [k: string]: any };

                /**
                 * Gets the type url for TypicalItem
                 * @param [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
                 * @returns The type url
                 */
                public static getTypeUrl(prefix?: string): string;
            }

            /** Properties of a StringItem. */
            interface IStringItem {

                /** StringItem code */
                code?: (string|null);

                /** StringItem city */
                city?: (string|null);

                /** StringItem country */
                country?: (string|null);

                /** StringItem segment */
                segment?: (string|null);

                /** StringItem status */
                status?: (string|null);

                /** Unknown fields preserved while decoding */
                $unknowns?: Uint8Array[];
            }

            /** Represents a StringItem. */
            class StringItem implements IStringItem {

                /**
                 * Constructs a new StringItem.
                 * @param [properties] Properties to set
                 */
                constructor(properties?: telepact.performance.v1.IStringItem);

                /** Unknown fields preserved while decoding */
                public $unknowns?: Uint8Array[];

                /** StringItem code. */
                public code: string;

                /** StringItem city. */
                public city: string;

                /** StringItem country. */
                public country: string;

                /** StringItem segment. */
                public segment: string;

                /** StringItem status. */
                public status: string;

                /**
                 * Creates a new StringItem instance using the specified properties.
                 * @param [properties] Properties to set
                 * @returns StringItem instance
                 */
                public static create(properties?: telepact.performance.v1.IStringItem): telepact.performance.v1.StringItem;

                /**
                 * Encodes the specified StringItem message. Does not implicitly {@link telepact.performance.v1.StringItem.verify|verify} messages.
                 * @param message StringItem message or plain object to encode
                 * @param [writer] Writer to encode to
                 * @returns Writer
                 */
                public static encode(message: telepact.performance.v1.IStringItem, writer?: $protobuf.Writer): $protobuf.Writer;

                /**
                 * Encodes the specified StringItem message, length delimited. Does not implicitly {@link telepact.performance.v1.StringItem.verify|verify} messages.
                 * @param message StringItem message or plain object to encode
                 * @param [writer] Writer to encode to
                 * @returns Writer
                 */
                public static encodeDelimited(message: telepact.performance.v1.IStringItem, writer?: $protobuf.Writer): $protobuf.Writer;

                /**
                 * Decodes a StringItem message from the specified reader or buffer.
                 * @param reader Reader or buffer to decode from
                 * @param [length] Message length if known beforehand
                 * @returns StringItem
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): telepact.performance.v1.StringItem;

                /**
                 * Decodes a StringItem message from the specified reader or buffer, length delimited.
                 * @param reader Reader or buffer to decode from
                 * @returns StringItem
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): telepact.performance.v1.StringItem;

                /**
                 * Verifies a StringItem message.
                 * @param message Plain object to verify
                 * @returns `null` if valid, otherwise the reason why it is not
                 */
                public static verify(message: { [k: string]: any }): (string|null);

                /**
                 * Creates a StringItem message from a plain object. Also converts values to their respective internal types.
                 * @param object Plain object
                 * @returns StringItem
                 */
                public static fromObject(object: { [k: string]: any }): telepact.performance.v1.StringItem;

                /**
                 * Creates a plain object from a StringItem message. Also converts values to other types if specified.
                 * @param message StringItem
                 * @param [options] Conversion options
                 * @returns Plain object
                 */
                public static toObject(message: telepact.performance.v1.StringItem, options?: $protobuf.IConversionOptions): { [k: string]: any };

                /**
                 * Converts this StringItem to JSON.
                 * @returns JSON object
                 */
                public toJSON(): { [k: string]: any };

                /**
                 * Gets the type url for StringItem
                 * @param [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
                 * @returns The type url
                 */
                public static getTypeUrl(prefix?: string): string;
            }

            /** Properties of a NumberItem. */
            interface INumberItem {

                /** NumberItem accountId */
                accountId?: (number|Long|null);

                /** NumberItem visits */
                visits?: (number|Long|null);

                /** NumberItem score */
                score?: (number|null);

                /** NumberItem balance */
                balance?: (number|null);

                /** NumberItem ratio */
                ratio?: (number|null);

                /** Unknown fields preserved while decoding */
                $unknowns?: Uint8Array[];
            }

            /** Represents a NumberItem. */
            class NumberItem implements INumberItem {

                /**
                 * Constructs a new NumberItem.
                 * @param [properties] Properties to set
                 */
                constructor(properties?: telepact.performance.v1.INumberItem);

                /** Unknown fields preserved while decoding */
                public $unknowns?: Uint8Array[];

                /** NumberItem accountId. */
                public accountId: (number|Long);

                /** NumberItem visits. */
                public visits: (number|Long);

                /** NumberItem score. */
                public score: number;

                /** NumberItem balance. */
                public balance: number;

                /** NumberItem ratio. */
                public ratio: number;

                /**
                 * Creates a new NumberItem instance using the specified properties.
                 * @param [properties] Properties to set
                 * @returns NumberItem instance
                 */
                public static create(properties?: telepact.performance.v1.INumberItem): telepact.performance.v1.NumberItem;

                /**
                 * Encodes the specified NumberItem message. Does not implicitly {@link telepact.performance.v1.NumberItem.verify|verify} messages.
                 * @param message NumberItem message or plain object to encode
                 * @param [writer] Writer to encode to
                 * @returns Writer
                 */
                public static encode(message: telepact.performance.v1.INumberItem, writer?: $protobuf.Writer): $protobuf.Writer;

                /**
                 * Encodes the specified NumberItem message, length delimited. Does not implicitly {@link telepact.performance.v1.NumberItem.verify|verify} messages.
                 * @param message NumberItem message or plain object to encode
                 * @param [writer] Writer to encode to
                 * @returns Writer
                 */
                public static encodeDelimited(message: telepact.performance.v1.INumberItem, writer?: $protobuf.Writer): $protobuf.Writer;

                /**
                 * Decodes a NumberItem message from the specified reader or buffer.
                 * @param reader Reader or buffer to decode from
                 * @param [length] Message length if known beforehand
                 * @returns NumberItem
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): telepact.performance.v1.NumberItem;

                /**
                 * Decodes a NumberItem message from the specified reader or buffer, length delimited.
                 * @param reader Reader or buffer to decode from
                 * @returns NumberItem
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): telepact.performance.v1.NumberItem;

                /**
                 * Verifies a NumberItem message.
                 * @param message Plain object to verify
                 * @returns `null` if valid, otherwise the reason why it is not
                 */
                public static verify(message: { [k: string]: any }): (string|null);

                /**
                 * Creates a NumberItem message from a plain object. Also converts values to their respective internal types.
                 * @param object Plain object
                 * @returns NumberItem
                 */
                public static fromObject(object: { [k: string]: any }): telepact.performance.v1.NumberItem;

                /**
                 * Creates a plain object from a NumberItem message. Also converts values to other types if specified.
                 * @param message NumberItem
                 * @param [options] Conversion options
                 * @returns Plain object
                 */
                public static toObject(message: telepact.performance.v1.NumberItem, options?: $protobuf.IConversionOptions): { [k: string]: any };

                /**
                 * Converts this NumberItem to JSON.
                 * @returns JSON object
                 */
                public toJSON(): { [k: string]: any };

                /**
                 * Gets the type url for NumberItem
                 * @param [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
                 * @returns The type url
                 */
                public static getTypeUrl(prefix?: string): string;
            }

            /** Properties of a TypicalRequest. */
            interface ITypicalRequest {

                /** TypicalRequest items */
                items?: (telepact.performance.v1.ITypicalItem[]|null);

                /** Unknown fields preserved while decoding */
                $unknowns?: Uint8Array[];
            }

            /** Represents a TypicalRequest. */
            class TypicalRequest implements ITypicalRequest {

                /**
                 * Constructs a new TypicalRequest.
                 * @param [properties] Properties to set
                 */
                constructor(properties?: telepact.performance.v1.ITypicalRequest);

                /** Unknown fields preserved while decoding */
                public $unknowns?: Uint8Array[];

                /** TypicalRequest items. */
                public items: telepact.performance.v1.ITypicalItem[];

                /**
                 * Creates a new TypicalRequest instance using the specified properties.
                 * @param [properties] Properties to set
                 * @returns TypicalRequest instance
                 */
                public static create(properties?: telepact.performance.v1.ITypicalRequest): telepact.performance.v1.TypicalRequest;

                /**
                 * Encodes the specified TypicalRequest message. Does not implicitly {@link telepact.performance.v1.TypicalRequest.verify|verify} messages.
                 * @param message TypicalRequest message or plain object to encode
                 * @param [writer] Writer to encode to
                 * @returns Writer
                 */
                public static encode(message: telepact.performance.v1.ITypicalRequest, writer?: $protobuf.Writer): $protobuf.Writer;

                /**
                 * Encodes the specified TypicalRequest message, length delimited. Does not implicitly {@link telepact.performance.v1.TypicalRequest.verify|verify} messages.
                 * @param message TypicalRequest message or plain object to encode
                 * @param [writer] Writer to encode to
                 * @returns Writer
                 */
                public static encodeDelimited(message: telepact.performance.v1.ITypicalRequest, writer?: $protobuf.Writer): $protobuf.Writer;

                /**
                 * Decodes a TypicalRequest message from the specified reader or buffer.
                 * @param reader Reader or buffer to decode from
                 * @param [length] Message length if known beforehand
                 * @returns TypicalRequest
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): telepact.performance.v1.TypicalRequest;

                /**
                 * Decodes a TypicalRequest message from the specified reader or buffer, length delimited.
                 * @param reader Reader or buffer to decode from
                 * @returns TypicalRequest
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): telepact.performance.v1.TypicalRequest;

                /**
                 * Verifies a TypicalRequest message.
                 * @param message Plain object to verify
                 * @returns `null` if valid, otherwise the reason why it is not
                 */
                public static verify(message: { [k: string]: any }): (string|null);

                /**
                 * Creates a TypicalRequest message from a plain object. Also converts values to their respective internal types.
                 * @param object Plain object
                 * @returns TypicalRequest
                 */
                public static fromObject(object: { [k: string]: any }): telepact.performance.v1.TypicalRequest;

                /**
                 * Creates a plain object from a TypicalRequest message. Also converts values to other types if specified.
                 * @param message TypicalRequest
                 * @param [options] Conversion options
                 * @returns Plain object
                 */
                public static toObject(message: telepact.performance.v1.TypicalRequest, options?: $protobuf.IConversionOptions): { [k: string]: any };

                /**
                 * Converts this TypicalRequest to JSON.
                 * @returns JSON object
                 */
                public toJSON(): { [k: string]: any };

                /**
                 * Gets the type url for TypicalRequest
                 * @param [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
                 * @returns The type url
                 */
                public static getTypeUrl(prefix?: string): string;
            }

            /** Properties of a TypicalResponse. */
            interface ITypicalResponse {

                /** TypicalResponse items */
                items?: (telepact.performance.v1.ITypicalItem[]|null);

                /** Unknown fields preserved while decoding */
                $unknowns?: Uint8Array[];
            }

            /** Represents a TypicalResponse. */
            class TypicalResponse implements ITypicalResponse {

                /**
                 * Constructs a new TypicalResponse.
                 * @param [properties] Properties to set
                 */
                constructor(properties?: telepact.performance.v1.ITypicalResponse);

                /** Unknown fields preserved while decoding */
                public $unknowns?: Uint8Array[];

                /** TypicalResponse items. */
                public items: telepact.performance.v1.ITypicalItem[];

                /**
                 * Creates a new TypicalResponse instance using the specified properties.
                 * @param [properties] Properties to set
                 * @returns TypicalResponse instance
                 */
                public static create(properties?: telepact.performance.v1.ITypicalResponse): telepact.performance.v1.TypicalResponse;

                /**
                 * Encodes the specified TypicalResponse message. Does not implicitly {@link telepact.performance.v1.TypicalResponse.verify|verify} messages.
                 * @param message TypicalResponse message or plain object to encode
                 * @param [writer] Writer to encode to
                 * @returns Writer
                 */
                public static encode(message: telepact.performance.v1.ITypicalResponse, writer?: $protobuf.Writer): $protobuf.Writer;

                /**
                 * Encodes the specified TypicalResponse message, length delimited. Does not implicitly {@link telepact.performance.v1.TypicalResponse.verify|verify} messages.
                 * @param message TypicalResponse message or plain object to encode
                 * @param [writer] Writer to encode to
                 * @returns Writer
                 */
                public static encodeDelimited(message: telepact.performance.v1.ITypicalResponse, writer?: $protobuf.Writer): $protobuf.Writer;

                /**
                 * Decodes a TypicalResponse message from the specified reader or buffer.
                 * @param reader Reader or buffer to decode from
                 * @param [length] Message length if known beforehand
                 * @returns TypicalResponse
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): telepact.performance.v1.TypicalResponse;

                /**
                 * Decodes a TypicalResponse message from the specified reader or buffer, length delimited.
                 * @param reader Reader or buffer to decode from
                 * @returns TypicalResponse
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): telepact.performance.v1.TypicalResponse;

                /**
                 * Verifies a TypicalResponse message.
                 * @param message Plain object to verify
                 * @returns `null` if valid, otherwise the reason why it is not
                 */
                public static verify(message: { [k: string]: any }): (string|null);

                /**
                 * Creates a TypicalResponse message from a plain object. Also converts values to their respective internal types.
                 * @param object Plain object
                 * @returns TypicalResponse
                 */
                public static fromObject(object: { [k: string]: any }): telepact.performance.v1.TypicalResponse;

                /**
                 * Creates a plain object from a TypicalResponse message. Also converts values to other types if specified.
                 * @param message TypicalResponse
                 * @param [options] Conversion options
                 * @returns Plain object
                 */
                public static toObject(message: telepact.performance.v1.TypicalResponse, options?: $protobuf.IConversionOptions): { [k: string]: any };

                /**
                 * Converts this TypicalResponse to JSON.
                 * @returns JSON object
                 */
                public toJSON(): { [k: string]: any };

                /**
                 * Gets the type url for TypicalResponse
                 * @param [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
                 * @returns The type url
                 */
                public static getTypeUrl(prefix?: string): string;
            }

            /** Properties of a StringsRequest. */
            interface IStringsRequest {

                /** StringsRequest items */
                items?: (telepact.performance.v1.IStringItem[]|null);

                /** Unknown fields preserved while decoding */
                $unknowns?: Uint8Array[];
            }

            /** Represents a StringsRequest. */
            class StringsRequest implements IStringsRequest {

                /**
                 * Constructs a new StringsRequest.
                 * @param [properties] Properties to set
                 */
                constructor(properties?: telepact.performance.v1.IStringsRequest);

                /** Unknown fields preserved while decoding */
                public $unknowns?: Uint8Array[];

                /** StringsRequest items. */
                public items: telepact.performance.v1.IStringItem[];

                /**
                 * Creates a new StringsRequest instance using the specified properties.
                 * @param [properties] Properties to set
                 * @returns StringsRequest instance
                 */
                public static create(properties?: telepact.performance.v1.IStringsRequest): telepact.performance.v1.StringsRequest;

                /**
                 * Encodes the specified StringsRequest message. Does not implicitly {@link telepact.performance.v1.StringsRequest.verify|verify} messages.
                 * @param message StringsRequest message or plain object to encode
                 * @param [writer] Writer to encode to
                 * @returns Writer
                 */
                public static encode(message: telepact.performance.v1.IStringsRequest, writer?: $protobuf.Writer): $protobuf.Writer;

                /**
                 * Encodes the specified StringsRequest message, length delimited. Does not implicitly {@link telepact.performance.v1.StringsRequest.verify|verify} messages.
                 * @param message StringsRequest message or plain object to encode
                 * @param [writer] Writer to encode to
                 * @returns Writer
                 */
                public static encodeDelimited(message: telepact.performance.v1.IStringsRequest, writer?: $protobuf.Writer): $protobuf.Writer;

                /**
                 * Decodes a StringsRequest message from the specified reader or buffer.
                 * @param reader Reader or buffer to decode from
                 * @param [length] Message length if known beforehand
                 * @returns StringsRequest
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): telepact.performance.v1.StringsRequest;

                /**
                 * Decodes a StringsRequest message from the specified reader or buffer, length delimited.
                 * @param reader Reader or buffer to decode from
                 * @returns StringsRequest
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): telepact.performance.v1.StringsRequest;

                /**
                 * Verifies a StringsRequest message.
                 * @param message Plain object to verify
                 * @returns `null` if valid, otherwise the reason why it is not
                 */
                public static verify(message: { [k: string]: any }): (string|null);

                /**
                 * Creates a StringsRequest message from a plain object. Also converts values to their respective internal types.
                 * @param object Plain object
                 * @returns StringsRequest
                 */
                public static fromObject(object: { [k: string]: any }): telepact.performance.v1.StringsRequest;

                /**
                 * Creates a plain object from a StringsRequest message. Also converts values to other types if specified.
                 * @param message StringsRequest
                 * @param [options] Conversion options
                 * @returns Plain object
                 */
                public static toObject(message: telepact.performance.v1.StringsRequest, options?: $protobuf.IConversionOptions): { [k: string]: any };

                /**
                 * Converts this StringsRequest to JSON.
                 * @returns JSON object
                 */
                public toJSON(): { [k: string]: any };

                /**
                 * Gets the type url for StringsRequest
                 * @param [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
                 * @returns The type url
                 */
                public static getTypeUrl(prefix?: string): string;
            }

            /** Properties of a StringsResponse. */
            interface IStringsResponse {

                /** StringsResponse items */
                items?: (telepact.performance.v1.IStringItem[]|null);

                /** Unknown fields preserved while decoding */
                $unknowns?: Uint8Array[];
            }

            /** Represents a StringsResponse. */
            class StringsResponse implements IStringsResponse {

                /**
                 * Constructs a new StringsResponse.
                 * @param [properties] Properties to set
                 */
                constructor(properties?: telepact.performance.v1.IStringsResponse);

                /** Unknown fields preserved while decoding */
                public $unknowns?: Uint8Array[];

                /** StringsResponse items. */
                public items: telepact.performance.v1.IStringItem[];

                /**
                 * Creates a new StringsResponse instance using the specified properties.
                 * @param [properties] Properties to set
                 * @returns StringsResponse instance
                 */
                public static create(properties?: telepact.performance.v1.IStringsResponse): telepact.performance.v1.StringsResponse;

                /**
                 * Encodes the specified StringsResponse message. Does not implicitly {@link telepact.performance.v1.StringsResponse.verify|verify} messages.
                 * @param message StringsResponse message or plain object to encode
                 * @param [writer] Writer to encode to
                 * @returns Writer
                 */
                public static encode(message: telepact.performance.v1.IStringsResponse, writer?: $protobuf.Writer): $protobuf.Writer;

                /**
                 * Encodes the specified StringsResponse message, length delimited. Does not implicitly {@link telepact.performance.v1.StringsResponse.verify|verify} messages.
                 * @param message StringsResponse message or plain object to encode
                 * @param [writer] Writer to encode to
                 * @returns Writer
                 */
                public static encodeDelimited(message: telepact.performance.v1.IStringsResponse, writer?: $protobuf.Writer): $protobuf.Writer;

                /**
                 * Decodes a StringsResponse message from the specified reader or buffer.
                 * @param reader Reader or buffer to decode from
                 * @param [length] Message length if known beforehand
                 * @returns StringsResponse
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): telepact.performance.v1.StringsResponse;

                /**
                 * Decodes a StringsResponse message from the specified reader or buffer, length delimited.
                 * @param reader Reader or buffer to decode from
                 * @returns StringsResponse
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): telepact.performance.v1.StringsResponse;

                /**
                 * Verifies a StringsResponse message.
                 * @param message Plain object to verify
                 * @returns `null` if valid, otherwise the reason why it is not
                 */
                public static verify(message: { [k: string]: any }): (string|null);

                /**
                 * Creates a StringsResponse message from a plain object. Also converts values to their respective internal types.
                 * @param object Plain object
                 * @returns StringsResponse
                 */
                public static fromObject(object: { [k: string]: any }): telepact.performance.v1.StringsResponse;

                /**
                 * Creates a plain object from a StringsResponse message. Also converts values to other types if specified.
                 * @param message StringsResponse
                 * @param [options] Conversion options
                 * @returns Plain object
                 */
                public static toObject(message: telepact.performance.v1.StringsResponse, options?: $protobuf.IConversionOptions): { [k: string]: any };

                /**
                 * Converts this StringsResponse to JSON.
                 * @returns JSON object
                 */
                public toJSON(): { [k: string]: any };

                /**
                 * Gets the type url for StringsResponse
                 * @param [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
                 * @returns The type url
                 */
                public static getTypeUrl(prefix?: string): string;
            }

            /** Properties of a NumbersRequest. */
            interface INumbersRequest {

                /** NumbersRequest items */
                items?: (telepact.performance.v1.INumberItem[]|null);

                /** Unknown fields preserved while decoding */
                $unknowns?: Uint8Array[];
            }

            /** Represents a NumbersRequest. */
            class NumbersRequest implements INumbersRequest {

                /**
                 * Constructs a new NumbersRequest.
                 * @param [properties] Properties to set
                 */
                constructor(properties?: telepact.performance.v1.INumbersRequest);

                /** Unknown fields preserved while decoding */
                public $unknowns?: Uint8Array[];

                /** NumbersRequest items. */
                public items: telepact.performance.v1.INumberItem[];

                /**
                 * Creates a new NumbersRequest instance using the specified properties.
                 * @param [properties] Properties to set
                 * @returns NumbersRequest instance
                 */
                public static create(properties?: telepact.performance.v1.INumbersRequest): telepact.performance.v1.NumbersRequest;

                /**
                 * Encodes the specified NumbersRequest message. Does not implicitly {@link telepact.performance.v1.NumbersRequest.verify|verify} messages.
                 * @param message NumbersRequest message or plain object to encode
                 * @param [writer] Writer to encode to
                 * @returns Writer
                 */
                public static encode(message: telepact.performance.v1.INumbersRequest, writer?: $protobuf.Writer): $protobuf.Writer;

                /**
                 * Encodes the specified NumbersRequest message, length delimited. Does not implicitly {@link telepact.performance.v1.NumbersRequest.verify|verify} messages.
                 * @param message NumbersRequest message or plain object to encode
                 * @param [writer] Writer to encode to
                 * @returns Writer
                 */
                public static encodeDelimited(message: telepact.performance.v1.INumbersRequest, writer?: $protobuf.Writer): $protobuf.Writer;

                /**
                 * Decodes a NumbersRequest message from the specified reader or buffer.
                 * @param reader Reader or buffer to decode from
                 * @param [length] Message length if known beforehand
                 * @returns NumbersRequest
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): telepact.performance.v1.NumbersRequest;

                /**
                 * Decodes a NumbersRequest message from the specified reader or buffer, length delimited.
                 * @param reader Reader or buffer to decode from
                 * @returns NumbersRequest
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): telepact.performance.v1.NumbersRequest;

                /**
                 * Verifies a NumbersRequest message.
                 * @param message Plain object to verify
                 * @returns `null` if valid, otherwise the reason why it is not
                 */
                public static verify(message: { [k: string]: any }): (string|null);

                /**
                 * Creates a NumbersRequest message from a plain object. Also converts values to their respective internal types.
                 * @param object Plain object
                 * @returns NumbersRequest
                 */
                public static fromObject(object: { [k: string]: any }): telepact.performance.v1.NumbersRequest;

                /**
                 * Creates a plain object from a NumbersRequest message. Also converts values to other types if specified.
                 * @param message NumbersRequest
                 * @param [options] Conversion options
                 * @returns Plain object
                 */
                public static toObject(message: telepact.performance.v1.NumbersRequest, options?: $protobuf.IConversionOptions): { [k: string]: any };

                /**
                 * Converts this NumbersRequest to JSON.
                 * @returns JSON object
                 */
                public toJSON(): { [k: string]: any };

                /**
                 * Gets the type url for NumbersRequest
                 * @param [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
                 * @returns The type url
                 */
                public static getTypeUrl(prefix?: string): string;
            }

            /** Properties of a NumbersResponse. */
            interface INumbersResponse {

                /** NumbersResponse items */
                items?: (telepact.performance.v1.INumberItem[]|null);

                /** Unknown fields preserved while decoding */
                $unknowns?: Uint8Array[];
            }

            /** Represents a NumbersResponse. */
            class NumbersResponse implements INumbersResponse {

                /**
                 * Constructs a new NumbersResponse.
                 * @param [properties] Properties to set
                 */
                constructor(properties?: telepact.performance.v1.INumbersResponse);

                /** Unknown fields preserved while decoding */
                public $unknowns?: Uint8Array[];

                /** NumbersResponse items. */
                public items: telepact.performance.v1.INumberItem[];

                /**
                 * Creates a new NumbersResponse instance using the specified properties.
                 * @param [properties] Properties to set
                 * @returns NumbersResponse instance
                 */
                public static create(properties?: telepact.performance.v1.INumbersResponse): telepact.performance.v1.NumbersResponse;

                /**
                 * Encodes the specified NumbersResponse message. Does not implicitly {@link telepact.performance.v1.NumbersResponse.verify|verify} messages.
                 * @param message NumbersResponse message or plain object to encode
                 * @param [writer] Writer to encode to
                 * @returns Writer
                 */
                public static encode(message: telepact.performance.v1.INumbersResponse, writer?: $protobuf.Writer): $protobuf.Writer;

                /**
                 * Encodes the specified NumbersResponse message, length delimited. Does not implicitly {@link telepact.performance.v1.NumbersResponse.verify|verify} messages.
                 * @param message NumbersResponse message or plain object to encode
                 * @param [writer] Writer to encode to
                 * @returns Writer
                 */
                public static encodeDelimited(message: telepact.performance.v1.INumbersResponse, writer?: $protobuf.Writer): $protobuf.Writer;

                /**
                 * Decodes a NumbersResponse message from the specified reader or buffer.
                 * @param reader Reader or buffer to decode from
                 * @param [length] Message length if known beforehand
                 * @returns NumbersResponse
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): telepact.performance.v1.NumbersResponse;

                /**
                 * Decodes a NumbersResponse message from the specified reader or buffer, length delimited.
                 * @param reader Reader or buffer to decode from
                 * @returns NumbersResponse
                 * @throws {Error} If the payload is not a reader or valid buffer
                 * @throws {$protobuf.util.ProtocolError} If required fields are missing
                 */
                public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): telepact.performance.v1.NumbersResponse;

                /**
                 * Verifies a NumbersResponse message.
                 * @param message Plain object to verify
                 * @returns `null` if valid, otherwise the reason why it is not
                 */
                public static verify(message: { [k: string]: any }): (string|null);

                /**
                 * Creates a NumbersResponse message from a plain object. Also converts values to their respective internal types.
                 * @param object Plain object
                 * @returns NumbersResponse
                 */
                public static fromObject(object: { [k: string]: any }): telepact.performance.v1.NumbersResponse;

                /**
                 * Creates a plain object from a NumbersResponse message. Also converts values to other types if specified.
                 * @param message NumbersResponse
                 * @param [options] Conversion options
                 * @returns Plain object
                 */
                public static toObject(message: telepact.performance.v1.NumbersResponse, options?: $protobuf.IConversionOptions): { [k: string]: any };

                /**
                 * Converts this NumbersResponse to JSON.
                 * @returns JSON object
                 */
                public toJSON(): { [k: string]: any };

                /**
                 * Gets the type url for NumbersResponse
                 * @param [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
                 * @returns The type url
                 */
                public static getTypeUrl(prefix?: string): string;
            }

            /** Represents a PerformanceService */
            class PerformanceService extends $protobuf.rpc.Service {

                /**
                 * Constructs a new PerformanceService service.
                 * @param rpcImpl RPC implementation
                 * @param [requestDelimited=false] Whether requests are length-delimited
                 * @param [responseDelimited=false] Whether responses are length-delimited
                 */
                constructor(rpcImpl: $protobuf.RPCImpl, requestDelimited?: boolean, responseDelimited?: boolean);

                /**
                 * Creates new PerformanceService service using the specified rpc implementation.
                 * @param rpcImpl RPC implementation
                 * @param [requestDelimited=false] Whether requests are length-delimited
                 * @param [responseDelimited=false] Whether responses are length-delimited
                 * @returns RPC service. Useful where requests and/or responses are streamed.
                 */
                public static create(rpcImpl: $protobuf.RPCImpl, requestDelimited?: boolean, responseDelimited?: boolean): PerformanceService;

                /**
                 * Calls RoundTripTypical.
                 * @param request TypicalRequest message or plain object
                 * @param callback Node-style callback called with the error, if any, and TypicalResponse
                 */
                public roundTripTypical(request: telepact.performance.v1.ITypicalRequest, callback: telepact.performance.v1.PerformanceService.RoundTripTypicalCallback): void;

                /**
                 * Calls RoundTripTypical.
                 * @param request TypicalRequest message or plain object
                 * @returns Promise
                 */
                public roundTripTypical(request: telepact.performance.v1.ITypicalRequest): Promise<telepact.performance.v1.TypicalResponse>;

                /**
                 * Calls RoundTripStrings.
                 * @param request StringsRequest message or plain object
                 * @param callback Node-style callback called with the error, if any, and StringsResponse
                 */
                public roundTripStrings(request: telepact.performance.v1.IStringsRequest, callback: telepact.performance.v1.PerformanceService.RoundTripStringsCallback): void;

                /**
                 * Calls RoundTripStrings.
                 * @param request StringsRequest message or plain object
                 * @returns Promise
                 */
                public roundTripStrings(request: telepact.performance.v1.IStringsRequest): Promise<telepact.performance.v1.StringsResponse>;

                /**
                 * Calls RoundTripNumbers.
                 * @param request NumbersRequest message or plain object
                 * @param callback Node-style callback called with the error, if any, and NumbersResponse
                 */
                public roundTripNumbers(request: telepact.performance.v1.INumbersRequest, callback: telepact.performance.v1.PerformanceService.RoundTripNumbersCallback): void;

                /**
                 * Calls RoundTripNumbers.
                 * @param request NumbersRequest message or plain object
                 * @returns Promise
                 */
                public roundTripNumbers(request: telepact.performance.v1.INumbersRequest): Promise<telepact.performance.v1.NumbersResponse>;
            }

            namespace PerformanceService {

                /**
                 * Callback as used by {@link telepact.performance.v1.PerformanceService#roundTripTypical}.
                 * @param error Error, if any
                 * @param [response] TypicalResponse
                 */
                type RoundTripTypicalCallback = (error: (Error|null), response?: telepact.performance.v1.TypicalResponse) => void;

                /**
                 * Callback as used by {@link telepact.performance.v1.PerformanceService#roundTripStrings}.
                 * @param error Error, if any
                 * @param [response] StringsResponse
                 */
                type RoundTripStringsCallback = (error: (Error|null), response?: telepact.performance.v1.StringsResponse) => void;

                /**
                 * Callback as used by {@link telepact.performance.v1.PerformanceService#roundTripNumbers}.
                 * @param error Error, if any
                 * @param [response] NumbersResponse
                 */
                type RoundTripNumbersCallback = (error: (Error|null), response?: telepact.performance.v1.NumbersResponse) => void;
            }
        }
    }
}
