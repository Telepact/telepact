//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.types;

public class TError {
    public final String name;
    public final TUnion errors;

    public TError(String name, TUnion errors) {
        this.name = name;
        this.errors = errors;
    }
}
