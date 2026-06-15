#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from typing import TypeVar, Generic, NamedTuple

T = TypeVar('T')

class TypedMessage(NamedTuple, Generic[T]):
    headers: dict[str, object]
    body: T