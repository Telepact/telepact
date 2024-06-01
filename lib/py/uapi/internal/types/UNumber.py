from typing import List, Dict
from uapi import RandomGenerator
from uapi.internal.validation import ValidationFailure
from uapi.internal.types import UType, UTypeDeclaration
from uapi.internal.generation import GenerateRandomNumber
from uapi.internal.validation import ValidateNumber


class UNumber(UType):
    _NUMBER_NAME: str = "Number"

    def getTypeParameterCount(self) -> int:
        return 0

    def validate(self, value: object, select: Dict[str, object], fn: str,
                 typeParameters: List[UTypeDeclaration], generics: List[UTypeDeclaration]) -> List[ValidationFailure]:
        return ValidateNumber.validateNumber(value)

    def generateRandomValue(self, blueprintValue: object, useBlueprintValue: bool,
                            includeOptionalFields: bool, randomizeOptionalFields: bool,
                            typeParameters: List[UTypeDeclaration], generics: List[UTypeDeclaration],
                            randomGenerator: RandomGenerator) -> object:
        return GenerateRandomNumber.generateRandomNumber(blueprintValue, useBlueprintValue, randomGenerator)

    def getName(self, generics: List[UTypeDeclaration]) -> str:
        return self._NUMBER_NAME
