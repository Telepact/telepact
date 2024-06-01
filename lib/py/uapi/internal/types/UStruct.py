from typing import List, Dict
from uapi import RandomGenerator
from uapi.internal.validation import ValidationFailure
from uapi.internal.types import UType, UFieldDeclaration, UTypeDeclaration
from uapi.internal.generation import GenerateRandomStruct
from uapi.internal.validation import ValidateStruct


class UStruct(UType):
    _STRUCT_NAME: str = "Object"

    def __init__(self, name: str, fields: Dict[str, UFieldDeclaration], typeParameterCount: int) -> None:
        self.name = name
        self.fields = fields
        self.typeParameterCount = typeParameterCount

    def getTypeParameterCount(self) -> int:
        return self.typeParameterCount

    def validate(self, value: object, select: Dict[str, object], fn: str,
                 typeParameters: List[UTypeDeclaration], generics: List[UTypeDeclaration]) -> List[ValidationFailure]:
        return ValidateStruct.validateStruct(value, select, fn, typeParameters, generics, self.name, self.fields)

    def generateRandomValue(self, blueprintValue: object, useBlueprintValue: bool,
                            includeOptionalFields: bool, randomizeOptionalFields: bool,
                            typeParameters: List[UTypeDeclaration], generics: List[UTypeDeclaration],
                            random: RandomGenerator) -> object:
        return GenerateRandomStruct.generateRandomStruct(blueprintValue, useBlueprintValue, includeOptionalFields,
                                                         randomizeOptionalFields, typeParameters, generics, random,
                                                         self.fields)

    def getName(self, generics: List[UTypeDeclaration]) -> str:
        return self._STRUCT_NAME
