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

export class ValidateContext {
    path: string[];
    select: { [key: string]: any } | null;
    fn: string | null;
    coerceBase64: boolean;
    base64Coercions: Record<string, object>;
    bytesCoercions: Record<string, object>;

    constructor(
        select: { [key: string]: any } | null, 
        fn: string | null, 
        coerceBase64: boolean,
    ) {
        this.path = [];
        this.select = select;
        this.fn = fn;
        this.coerceBase64 = coerceBase64;
        this.base64Coercions = {};
        this.bytesCoercions = {};
    }
}
