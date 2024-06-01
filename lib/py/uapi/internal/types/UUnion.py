from typing import List, Dict, Any
from uapi import RandomGenerator
from uapi.internal.types import UType, UStruct
from uapi.internal.validation import ValidationFailure, validateUnion
from uapi.internal.generation import GenerateRandomUnion, generateRandomUnion


class UUnion(UType):
    _UNION_NAME: str = "Object"

    def __init__(self, name: str, cases: Dict[str, UStruct], caseIndices: Dict[str, int], typeParameterCount: int) -> None:
        self.name = name
        self.cases = cases
        self.caseIndices = caseIndices
        self.typeParameterCount = typeParameterCount

    def getTypeParameterCount(self) -> int:
        return self.typeParameterCount

    def validate(self, value: Any, select: Dict[str, Any], fn: str, typeParameters: List[UTypeDeclaration], generics: List[UTypeDeclaration]) -> List[ValidationFailure]:
        return validateUnion(value, select, fn, typeParameters, generics, self.name, self.cases)

    def generateRandomValue(self, blueprintValue: Any, useBlueprintValue: bool, includeOptionalFields: bool, randomizeOptionalFields: bool, typeParameters: List[UTypeDeclaration], generics: List[UTypeDeclaration], random: RandomGenerator) -> Any:
        return generateRandomUnion(blueprintValue, useBlueprintValue, includeOptionalFields, randomizeOptionalFields, typeParameters, generics, random, self.cases)

    def getName(self, generics: List[UTypeDeclaration]) -> str:
        return self._UNION_NAME
