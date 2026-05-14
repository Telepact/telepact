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

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class BinaryPackSite {

    public final List<String> path;
    public final List<Integer> encodedPath;
    public final List<Object> header;

    public BinaryPackSite(List<Object> siteData, Map<String, Integer> binaryEncodingMap) {
        final var rawPath = (List<Object>) siteData.get(0);
        final var rawHeader = (List<Object>) siteData.get(1);
        this.path = new ArrayList<>();
        this.encodedPath = new ArrayList<>();
        for (final var segment : rawPath) {
            final var pathSegment = (String) segment;
            this.path.add(pathSegment);
            final var encodedSegment = binaryEncodingMap.get(pathSegment);
            if (encodedSegment == null) {
                throw new IllegalArgumentException("Missing binary encoding for packed path segment " + pathSegment);
            }
            this.encodedPath.add(encodedSegment);
        }
        this.header = cloneHeader(rawHeader);
    }

    public List<Object> toData() {
        return new ArrayList<>(List.of(new ArrayList<>(this.path), cloneHeader(this.header)));
    }

    public static List<Object> cloneHeader(List<Object> header) {
        final var clonedHeader = new ArrayList<Object>(header.size());
        for (final var entry : header) {
            if (entry instanceof final List<?> nestedHeader) {
                clonedHeader.add(cloneHeader((List<Object>) nestedHeader));
            } else {
                clonedHeader.add(entry);
            }
        }
        return clonedHeader;
    }
}
