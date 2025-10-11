from typing import TypeVar, Generic, NamedTuple

T = TypeVar('T')

class TypedMessage(NamedTuple, Generic[T]):
    headers: dict[str, object]
    body: T