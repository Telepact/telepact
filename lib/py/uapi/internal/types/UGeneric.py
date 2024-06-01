from typing import List, Dict
from uapi import RandomGenerator
from uapi.internal.validation import ValidationFailure
from uapi.internal.types import UTypeDeclaration, UType


class UGeneric(UType):
    def __init__(self, index: int):
        self.index = index

    def getTypeParameterCount(self) -> int:
        return 0

    def validate(self, value: object, select: Dict[str, object], fn: str,
                 typeParameters: List[UTypeDeclaration], generics: List[UTypeDeclaration]) -> List[ValidationFailure]:
        typeDeclaration = generics[self.index]
        return typeDeclaration.validate(value, select, fn, [])

    def generateRandomValue(self, blueprintValue: object, useBlueprintValue: bool,
                            includeOptionalFields: bool, randomizeOptionalFields: bool,
                            typeParameters: List[UTypeDeclaration], generics: List[UTypeDeclaration],
                            randomGenerator: RandomGenerator) -> object:
        genericTypeDeclaration = generics[self.index]
        return genericTypeDeclaration.generateRandomValue(blueprintValue, useBlueprintValue,
                                                          includeOptionalFields, randomizeOptionalFields, [],
                                                          randomGenerator)

    def getName(self, generics: List[UTypeDeclaration]) -> str:
        typeDeclaration = generics[self.index]
        return typeDeclaration.type.getName(generics)
