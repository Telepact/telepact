from typing import List, Dict
from uapi import RandomGenerator
from uapi.internal.validation import ValidationFailure
from uapi.internal.types import UType, UTypeDeclaration, validateSelect


class USelect(UType):
    _SELECT: str = "Object"

    def __init__(self, types: Dict[str, UType]) -> None:
        self.types = types

    def getTypeParameterCount(self) -> int:
        return 0

    def validate(self, givenObj: object, select: Dict[str, object], fn: str,
                 typeParameters: List[UTypeDeclaration], generics: List[UTypeDeclaration]) -> List[ValidationFailure]:
        return validateSelect(givenObj, select, fn, typeParameters, generics, self.types)

    def generateRandomValue(self, blueprintValue: object, useBlueprintValue: bool,
                            includeOptionalFields: bool, randomizeOptionalFields: bool,
                            typeParameters: List[UTypeDeclaration], generics: List[UTypeDeclaration],
                            randomGenerator: RandomGenerator) -> object:
        raise NotImplementedError("Not implemented")

    def getName(self, generics: List[UTypeDeclaration]) -> str:
        return self._SELECT
