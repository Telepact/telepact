//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

export interface TypedMessage<T> {
    headers: { [key: string]: any },
    body: T
}