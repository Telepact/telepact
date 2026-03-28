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

import { Base64Encoder } from "../../internal/binary/Base64Encoder";
import { clientBase64Decode } from "../../internal/binary/ClientBase64Decode";
import { clientBase64Encode } from "../../internal/binary/ClientBase64Encode";

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