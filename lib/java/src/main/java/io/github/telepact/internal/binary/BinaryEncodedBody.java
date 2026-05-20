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

package io.github.telepact.internal.binary;

import java.util.Map;

public class BinaryEncodedBody {
    public final Map<String, Object> value;
    public final BinaryEncoding binaryEncoding;

    public BinaryEncodedBody(Map<String, Object> value, BinaryEncoding binaryEncoding) {
        this.value = value;
        this.binaryEncoding = binaryEncoding;
    }
}
