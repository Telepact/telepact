from typing import Any, Dict, List, Union


def select_struct_fields(typeDeclaration: UTypeDeclaration, value: Any,
                         selectedStructFields: Dict[str, Any]) -> Any:
    typeDeclarationType = typeDeclaration.type
    typeDeclarationTypeParams = typeDeclaration.typeParameters

    if isinstance(typeDeclarationType, UStruct):
        fields = typeDeclarationType.fields
        structName = typeDeclarationType.name
        selectedFields = selectedStructFields.get(structName, [])
        valueAsMap = value
        finalMap = {}

        for fieldName, fieldValue in valueAsMap.items():
            if selectedFields == [] or fieldName in selectedFields:
                field = fields.get(fieldName)
                fieldTypeDeclaration = field.typeDeclaration
                valueWithSelectedFields = select_struct_fields(fieldTypeDeclaration, fieldValue,
                                                               selectedStructFields)

                finalMap[fieldName] = valueWithSelectedFields

        return finalMap
    elif isinstance(typeDeclarationType, UFn):
        valueAsMap = value
        unionCase, unionData = next(iter(valueAsMap.items()))

        fnName = typeDeclarationType.name
        fnCall = typeDeclarationType.call
        fnCallCases = fnCall.cases

        argStructReference = fnCallCases.get(unionCase)
        selectedFields = selectedStructFields.get(fnName, [])
        finalMap = {}

        for fieldName, fieldValue in unionData.items():
            if selectedFields == [] or fieldName in selectedFields:
                field = argStructReference.fields.get(fieldName)
                valueWithSelectedFields = select_struct_fields(field.typeDeclaration, fieldValue,
                                                               selectedStructFields)

                finalMap[fieldName] = valueWithSelectedFields

        return {unionCase: finalMap}
    elif isinstance(typeDeclarationType, UUnion):
        valueAsMap = value
        unionCase, unionData = next(iter(valueAsMap.items()))

        unionCases = typeDeclarationType.cases
        unionStructReference = unionCases.get(unionCase)
        unionStructRefFields = unionStructReference.fields
        defaultCasesToFields = {}

        for case, unionStruct in unionCases.items():
            unionStructFields = unionStruct.fields
            fields = list(unionStructFields.keys())
            defaultCasesToFields[case] = fields

        unionSelectedFields = selectedStructFields.get(
            typeDeclarationType.name, defaultCasesToFields)
        thisUnionCaseSelectedFieldsDefault = defaultCasesToFields.get(
            unionCase)
        selectedFields = unionSelectedFields.get(
            unionCase, thisUnionCaseSelectedFieldsDefault)

        finalMap = {}
        for fieldName, fieldValue in unionData.items():
            if selectedFields == [] or fieldName in selectedFields:
                field = unionStructRefFields.get(fieldName)
                valueWithSelectedFields = select_struct_fields(field.typeDeclaration, fieldValue,
                                                               selectedStructFields)
                finalMap[fieldName] = valueWithSelectedFields

        return {unionCase: finalMap}
    elif isinstance(typeDeclarationType, UObject):
        nestedTypeDeclaration = typeDeclarationTypeParams[0]
        valueAsMap = value

        finalMap = {}
        for key, nestedValue in valueAsMap.items():
            valueWithSelectedFields = select_struct_fields(nestedTypeDeclaration, nestedValue,
                                                           selectedStructFields)
            finalMap[key] = valueWithSelectedFields

        return finalMap
    elif isinstance(typeDeclarationType, UArray):
        nestedType = typeDeclarationTypeParams[0]
        valueAsList = value

        finalList = []
        for entry in valueAsList:
            valueWithSelectedFields = select_struct_fields(
                nestedType, entry, selectedStructFields)
            finalList.append(valueWithSelectedFields)

        return finalList
    else:
        return value
