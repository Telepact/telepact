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

import java.util.List;

/**
 * The strategy used by the client to maintain binary encodings compatible with
 * the server.
 */
public interface ClientBinaryStrategy {

    /**
     * Update the strategy according to a recent binary encoding checksum returned
     * by the server.
     * 
     * @param checksum
     */
    void updateChecksum(Integer checksum);

    /**
     * Get the current binary encoding strategy as a list of binary encoding
     * checksums that should be sent to the server.
     * 
     * @return
     */
    List<Integer> getCurrentChecksums();
}
