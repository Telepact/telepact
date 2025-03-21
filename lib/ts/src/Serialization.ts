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
