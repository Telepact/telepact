from typing import Dict, Any, List
from random import randint
from uapi.internal.types import UStruct, UTypeDeclaration
from uapi import RandomGenerator
from uapi.internal.generation.ConstructRandomStruct import constructRandomStruct


def constructRandomUnion(unionCasesReference: Dict[str, UStruct],
                         startingUnion: Dict[str, Any],
                         includeOptionalFields: bool,
                         randomizeOptionalFields: bool,
                         typeParameters: List[UTypeDeclaration],
                         randomGenerator: RandomGenerator) -> Dict[str, Any]:
    if not startingUnion:
        unionCase, unionData = sorted(unionCasesReference.items())[
            randint(0, len(unionCasesReference) - 1)]
        return {unionCase: constructRandomStruct(unionData.fields, {}, includeOptionalFields, randomizeOptionalFields, typeParameters, randomGenerator)}
    else:
        unionCase, unionStartingStruct = next(iter(startingUnion.items()))
        unionStructType = unionCasesReference[unionCase]
        return {unionCase: constructRandomStruct(unionStructType.fields, unionStartingStruct, includeOptionalFields, randomizeOptionalFields, typeParameters, randomGenerator)}
