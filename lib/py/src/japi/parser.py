from typing import Any
import json

class Type:
    def __init__(self) -> None:
        pass
    
    def getName(self):
        pass

class JsonNull(Type):
    def __init__(self) -> None:
        super().__init__()

    def getName(self):
        return "null"
    
class JsonBoolean(Type):
    def __init__(self) -> None:
        super().__init__()

    def getName(self):
        return "boolean"
    
class JsonInteger(Type):
    def __init__(self) -> None:
        super().__init__()

    def getName(self):
        return "integer"

class JsonNumber(Type):
    def __init__(self) -> None:
        super().__init__()
    
    def getName(self):
        return "string"

class JsonArray(Type):
    def __init__(self, nestedType: TypeDeclaration) -> None:
        super().__init__()
        self.nestedType = nestedType
    
    def getName(self):
        return "array"

class JsonObject(Type):
    def __init__(self, nestedType: TypeDeclaration) -> None:
        super().__init__()
        self.nestedType = nestedType
    
    def getName(self):
        return "object"

class Struct(Type):
    def __init__(self, name: str, fields: dict) -> None:
        super().__init__()
        self.name = name
        self.fields = fields

    def getName(self):
        return self.name
    
class Enum(Type):
    def __init__(self, name: str, fields: dict) -> None:
        super().__init__()
        self.name = name
        self.fields = fields

class JsonAny(Type):
    def __init__(self) -> None:
        super().__init__()

    def getName(self):
        return "any"
    
class TypeDeclaration:
    def __init__(self, t: Type, nullable: bool) -> None:
        self.type = t
        self.nullable = nullable

class Definition:
    def __init__(self) -> None:
        pass

    def getName(self):
        pass

class FieldDeclaration:
    def __init__(self, typeDeclaration: TypeDeclaration, optional: bool) -> None:
        self.typeDeclaration = typeDeclaration
        self.optional = optional

class FunctionDefinition(Definition):
    def __init__(self, name: str, inputStruct: Struct, outputStruct: Struct, allowedErrors: list[str]) -> None:
        super().__init__()
        self.name = name
        self.inputStruct = inputStruct
        self.allowedErrors = allowedErrors
    
    def getName(self):
        return self.name
    
class TypeDefinition(Definition):
    def __init__(self, name: str, t: Type) -> None:
        super().__init__()
        self.name = name
        self.type = t

    def getName(self):
        return self.name

class ErrorDefinition(Definition):
    def __init__(self, name: str, fields: dict) -> None:
        super().__init__()
        self.name = name
        self.fields = fields
    
    def getName(self):
        return self.name

class TitleDefinition(Definition):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name

    def getName(self):
        return self.name
    
class JapiParseError(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)

class Japi():
    def __init__(self, original: dict[str, Any], parsed: dict[str, Definition]) -> None:
        pass
    
def newJapi(japiAsJson: str) -> Japi:
    parsedDefinitions = dict[str, Definition]

    japiAsJsonPython = json.loads(japiAsJson)

    
    