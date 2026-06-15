//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { Base64Encoder } from "../../internal/binary/Base64Encoder.js";
import { clientBase64Decode } from "../../internal/binary/ClientBase64Decode.js";
import { clientBase64Encode } from "../../internal/binary/ClientBase64Encode.js";

export class ClientBase64Encoder extends Base64Encoder {
    decode(message: object[]): object[] {
        clientBase64Decode(message);
        return message;
    }

    encode(message: object[]): object[] {
        clientBase64Encode(message);
        return message;
    }
}