//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.types;

public class TFieldDeclaration {
    public final String fieldName;
    public final TTypeDeclaration typeDeclaration;
    public final boolean optional;

    public TFieldDeclaration(
            String fieldName,
            TTypeDeclaration typeDeclaration,
            boolean optional) {
        this.fieldName = fieldName;
        this.typeDeclaration = typeDeclaration;
        this.optional = optional;
    }
}
