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

package io.github.telepact;

import java.util.Map;

public record SerializerMeasurement(
        String operation,
        long totalDurationNs,
        boolean binaryRequested,
        String transportEncoding,
        String protocolEncoding,
        boolean packed,
        boolean fellBackToJson,
        Map<String, Stage> stages) {

    public record Stage(long totalDurationNs, long count) {
    }
}
