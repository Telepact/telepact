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

import { BinaryEncoding } from '../../internal/binary/BinaryEncoding';
import { encodeBody } from '../../internal/binary/EncodeBody';
import { packBody } from '../../internal/binary/PackBody';
import { BinaryEncoderUnavailableError } from '../../internal/binary/BinaryEncoderUnavailableError';

export function serverBinaryEncode(message: any[], binaryEncoder: BinaryEncoding): any[] {
    const headers: { [key: string]: any } = message[0];
    const messageBody: { [key: string]: any } = message[1];
    const clientKnownBinaryChecksums: number[] | undefined = headers['_clientKnownBinaryChecksums'];
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

    let finalEncodedMessageBody: { [key: string]: any };
    if (headers['pac_'] === true) {
        finalEncodedMessageBody = packBody(encodedMessageBody);
    } else {
        finalEncodedMessageBody = encodedMessageBody;
    }

    return [headers, finalEncodedMessageBody];
}
