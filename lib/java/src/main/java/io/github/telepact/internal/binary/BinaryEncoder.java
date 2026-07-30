//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.binary;

import java.util.List;

public interface BinaryEncoder {
    List<Object> encode(List<Object> message);

    List<Object> decode(List<Object> message);
}