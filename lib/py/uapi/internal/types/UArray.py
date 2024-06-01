from typing import List, Dict
from uapi import RandomGenerator
from uapi.internal.validation import ValidationFailure
from uapi.internal.types import UType, UTypeDeclaration
from uapi.internal.generation import GenerateRandomArray
from uapi.internal.validation import ValidateArray


class UArray(UType):
    _ARRAY_NAME: str = "Array"

    def getTypeParameterCount(self) -> int:
        return 1

    def validate(self, value: object, select: Dict[str, object], fn: str,
                 typeParameters: List[UTypeDeclaration], generics: List[UTypeDeclaration]) -> List[ValidationFailure]:
        return ValidateArray.validateArray(value, select, fn, typeParameters, generics)

    def generateRandomValue(self, blueprintValue: object, useBlueprintValue: bool, includeOptionalFields: bool,
                            randomizeOptionalFields: bool, typeParameters: List[UTypeDeclaration],
                            generics: List[UTypeDeclaration], randomGenerator: RandomGenerator) -> object:
        return GenerateRandomArray.generateRandomArray(blueprintValue, useBlueprintValue, includeOptionalFields,
                                                       randomizeOptionalFields, typeParameters, generics,
                                                       randomGenerator)

    def getName(self, generics: List[UTypeDeclaration]) -> str:
        return self._ARRAY_NAME
