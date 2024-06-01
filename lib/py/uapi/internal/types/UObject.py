from typing import List, Dict
from uapi import RandomGenerator
from uapi.internal.types import UType
from uapi.internal.generation import GenerateRandomObject
from uapi.internal.validation import ValidateObject
from uapi.internal.validation.ValidationFailure import ValidationFailure


class UObject(UType):
    _OBJECT_NAME: str = "Object"

    def getTypeParameterCount(self) -> int:
        return 1

    def validate(self, value: object, select: Dict[str, object], fn: str,
                 typeParameters: List[UTypeDeclaration], generics: List[UTypeDeclaration]) -> List[ValidationFailure]:
        return ValidateObject.validateObject(value, select, fn, typeParameters, generics)

    def generateRandomValue(self, blueprintValue: object, useBlueprintValue: bool, includeOptionalFields: bool,
                            randomizeOptionalFields: bool, typeParameters: List[UTypeDeclaration],
                            generics: List[UTypeDeclaration], randomGenerator: RandomGenerator) -> object:
        return GenerateRandomObject.generateRandomObject(blueprintValue, useBlueprintValue, includeOptionalFields,
                                                         randomizeOptionalFields, typeParameters, generics,
                                                         randomGenerator)

    def getName(self, generics: List[UTypeDeclaration]) -> str:
        return self._OBJECT_NAME
