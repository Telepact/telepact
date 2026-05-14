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
import java.util.List;
import java.util.HashMap;
import java.util.stream.Collectors;

public class BinaryEncoding {

    public final Map<String, Integer> encodeMap;
    public final Map<Integer, String> decodeMap;
    public final Integer checksum;
    public final List<String> keys;
    public final List<Object> requestPlanDescriptors;
    public final List<Object> responsePlanDescriptors;

    public BinaryEncoding(Map<String, Integer> binaryEncodingMap, Integer checksum, List<String> keys, List<Object> requestPlanDescriptors, List<Object> responsePlanDescriptors) {
        this.encodeMap = binaryEncodingMap;
        this.decodeMap = binaryEncodingMap.entrySet().stream()
                .collect(Collectors.toMap(e -> e.getValue(), e -> e.getKey()));
        this.checksum = checksum;
        this.keys = keys;
        this.requestPlanDescriptors = requestPlanDescriptors;
        this.responsePlanDescriptors = responsePlanDescriptors;
    }

    public Map<String, Object> negotiationDescriptor(Integer functionId, boolean includeBundle) {
        final Map<String, Object> descriptor = new HashMap<>();
        descriptor.put("v", 1);
        if (functionId != null) {
            descriptor.put("p", functionId);
        }
        if (includeBundle) {
            descriptor.put("k", keys);
            descriptor.put("q", requestPlanDescriptors);
            descriptor.put("s", responsePlanDescriptors);
        }
        return descriptor;
    }

    public static BinaryEncoding fromNegotiationDescriptor(Integer checksum, Map<String, Object> descriptor) {
        final var keys = (List<String>) descriptor.get("k");
        final Map<String, Integer> encodingMap = new HashMap<>();
        for (int index = 0; index < keys.size(); index++) {
            encodingMap.put(keys.get(index), index);
        }
        final var requestPlanDescriptors = (List<Object>) descriptor.getOrDefault("q", List.of());
        final var responsePlanDescriptors = (List<Object>) descriptor.getOrDefault("s", List.of());
        return new BinaryEncoding(encodingMap, checksum, keys, requestPlanDescriptors, responsePlanDescriptors);
    }
}
