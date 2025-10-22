# Python to Go Port Progress

## Porting Instructions

1. Pick an unchecked row in the checklist.
2. Create the *.go file exactly how it is defined in the row.
3. Translate the python code in the corresponding *.py file to go code in the *.go file.
4. Mark the row as checked.

### Constraints:
- DO NOT make your own porting plan.
  - DO NOT waste time examining the entire partially ported go project.
  - Just stick to the outline in `PORT_PROGRESS.md` to guide port.
    - Every port should be a one-to-one file translation of python code to go code
- DO NOT deviate from the outline in `PORT_PROGRESS.md`
  - That means DO NOT add test files. Don't waste time trying to run tests.
- DO NOT rename the target go file as indicated in `PORT_PROGRESS.md`

### Encouragements
- Port at least 25 files at a time.

> **Status note:** The Go implementation consolidated several helpers (notably the generation and validation code) into the `telepact/internal/types` package. The checklist below reflects the actual Go locations for the Python functionality.


## Checklist

- [x] lib/py/telepact/Client.py → lib/go/telepact/Client.go
- [x] lib/py/telepact/DefaultSerialization.py → lib/go/telepact/DefaultSerialization.go
- [x] lib/py/telepact/Message.py → lib/go/telepact/Message.go
- [x] lib/py/telepact/MockServer.py → lib/go/telepact/MockServer.go
- [x] lib/py/telepact/MockTelepactSchema.py → lib/go/telepact/MockTelepactSchema.go
- [x] lib/py/telepact/RandomGenerator.py → lib/go/telepact/RandomGenerator.go
- [x] lib/py/telepact/Response.py → lib/go/telepact/Response.go
- [x] lib/py/telepact/Serialization.py → lib/go/telepact/Serialization.go
- [x] lib/py/telepact/SerializationError.py → lib/go/telepact/SerializationError.go
- [x] lib/py/telepact/Serializer.py → lib/go/telepact/Serializer.go
- [x] lib/py/telepact/Server.py → lib/go/telepact/Server.go
- [x] lib/py/telepact/TelepactError.py → lib/go/telepact/TelepactError.go
- [x] lib/py/telepact/TelepactSchema.py → lib/go/telepact/TelepactSchema.go
- [x] lib/py/telepact/TelepactSchemaFiles.py → lib/go/telepact/TelepactSchemaFiles.go
- [x] lib/py/telepact/TelepactSchemaParseError.py → lib/go/telepact/TelepactSchemaParseError.go
- [x] lib/py/telepact/TestClient.py → lib/go/telepact/TestClient.go
- [x] lib/py/telepact/TypedMessage.py → lib/go/telepact/TypedMessage.go
- [x] lib/py/telepact/internal/ClientHandleMessage.py → lib/go/telepact/internal/ClientHandleMessage.go
- [x] lib/py/telepact/internal/DeserializeInternal.py → lib/go/telepact/internal/DeserializeInternal.go
- [x] lib/py/telepact/internal/HandleMessage.py → lib/go/telepact/internal/HandleMessage.go
- [x] lib/py/telepact/internal/ParseRequestMessage.py → lib/go/telepact/internal/ParseRequestMessage.go
- [x] lib/py/telepact/internal/ProcessBytes.py → lib/go/telepact/internal/ProcessBytes.go
- [x] lib/py/telepact/internal/SelectStructFields.py → lib/go/telepact/internal/SelectStructFields.go
- [x] lib/py/telepact/internal/SerializeInternal.py → lib/go/telepact/internal/SerializeInternal.go
- [x] lib/py/telepact/internal/binary/Base64Encoder.py → lib/go/telepact/internal/binary/Base64Encoder.go
- [x] lib/py/telepact/internal/binary/BinaryEncoder.py → lib/go/telepact/internal/binary/BinaryEncoder.go
- [x] lib/py/telepact/internal/binary/BinaryEncoderUnavailableError.py → lib/go/telepact/internal/binary/BinaryEncoderUnavailableError.go
- [x] lib/py/telepact/internal/binary/BinaryEncoding.py → lib/go/telepact/internal/binary/BinaryEncoding.go
- [x] lib/py/telepact/internal/binary/BinaryEncodingCache.py → lib/go/telepact/internal/binary/BinaryEncodingCache.go
- [x] lib/py/telepact/internal/binary/BinaryEncodingMissing.py → lib/go/telepact/internal/binary/BinaryEncodingMissing.go
- [x] lib/py/telepact/internal/binary/BinaryPackNode.py → lib/go/telepact/internal/binary/BinaryPackNode.go
- [x] lib/py/telepact/internal/binary/CannotPack.py → lib/go/telepact/internal/binary/CannotPack.go
- [x] lib/py/telepact/internal/binary/ClientBase64Decode.py → lib/go/telepact/internal/binary/ClientBase64Decode.go
- [x] lib/py/telepact/internal/binary/ClientBase64Encode.py → lib/go/telepact/internal/binary/ClientBase64Encode.go
- [x] lib/py/telepact/internal/binary/ClientBase64Encoder.py → lib/go/telepact/internal/binary/ClientBase64Encoder.go
- [x] lib/py/telepact/internal/binary/ClientBinaryDecode.py → lib/go/telepact/internal/binary/ClientBinaryDecode.go
- [x] lib/py/telepact/internal/binary/ClientBinaryEncode.py → lib/go/telepact/internal/binary/ClientBinaryEncode.go
- [x] lib/py/telepact/internal/binary/ClientBinaryEncoder.py → lib/go/telepact/internal/binary/ClientBinaryEncoder.go
- [x] lib/py/telepact/internal/binary/ClientBinaryStrategy.py → lib/go/telepact/internal/binary/ClientBinaryStrategy.go
- [x] lib/py/telepact/internal/binary/ConstructBinaryEncoding.py → lib/go/telepact/internal/binary/ConstructBinaryEncoding.go
- [x] lib/py/telepact/internal/binary/CreateChecksum.py → lib/go/telepact/internal/binary/CreateChecksum.go
- [x] lib/py/telepact/internal/binary/DecodeBody.py → lib/go/telepact/internal/binary/DecodeBody.go
- [x] lib/py/telepact/internal/binary/DecodeKeys.py → lib/go/telepact/internal/binary/DecodeKeys.go
- [x] lib/py/telepact/internal/binary/DefaultBinaryEncodingCache.py → lib/go/telepact/internal/binary/DefaultBinaryEncodingCache.go
- [x] lib/py/telepact/internal/binary/EncodeBody.py → lib/go/telepact/internal/binary/EncodeBody.go
- [x] lib/py/telepact/internal/binary/EncodeKeys.py → lib/go/telepact/internal/binary/EncodeKeys.go
- [x] lib/py/telepact/internal/binary/Pack.py → lib/go/telepact/internal/binary/Pack.go
- [x] lib/py/telepact/internal/binary/PackBody.py → lib/go/telepact/internal/binary/PackBody.go
- [x] lib/py/telepact/internal/binary/PackList.py → lib/go/telepact/internal/binary/PackList.go
- [x] lib/py/telepact/internal/binary/PackMap.py → lib/go/telepact/internal/binary/PackMap.go
- [x] lib/py/telepact/internal/binary/ServerBase64Decode.py → lib/go/telepact/internal/binary/ServerBase64Decode.go
- [x] lib/py/telepact/internal/binary/ServerBase64Encode.py → lib/go/telepact/internal/binary/ServerBase64Encode.go
- [x] lib/py/telepact/internal/binary/ServerBase64Encoder.py → lib/go/telepact/internal/binary/ServerBase64Encoder.go
- [x] lib/py/telepact/internal/binary/ServerBinaryDecode.py → lib/go/telepact/internal/binary/ServerBinaryDecode.go
- [x] lib/py/telepact/internal/binary/ServerBinaryEncode.py → lib/go/telepact/internal/binary/ServerBinaryEncode.go
- [x] lib/py/telepact/internal/binary/ServerBinaryEncoder.py → lib/go/telepact/internal/binary/ServerBinaryEncoder.go
- [x] lib/py/telepact/internal/binary/Unpack.py → lib/go/telepact/internal/binary/Unpack.go
- [x] lib/py/telepact/internal/binary/UnpackBody.py → lib/go/telepact/internal/binary/UnpackBody.go
- [x] lib/py/telepact/internal/binary/UnpackList.py → lib/go/telepact/internal/binary/UnpackList.go
- [x] lib/py/telepact/internal/binary/UnpackMap.py → lib/go/telepact/internal/binary/UnpackMap.go
- [x] lib/py/telepact/internal/generation/GenerateContext.py → lib/go/telepact/internal/types/GenerateContext.go
- [x] lib/py/telepact/internal/generation/GenerateRandomAny.py → lib/go/telepact/internal/types/GenerateRandomAny.go
- [x] lib/py/telepact/internal/generation/GenerateRandomArray.py → lib/go/telepact/internal/types/GenerateRandomArray.go
- [x] lib/py/telepact/internal/generation/GenerateRandomBoolean.py → lib/go/telepact/internal/types/GenerateRandomBoolean.go
- [x] lib/py/telepact/internal/generation/GenerateRandomBytes.py → lib/go/telepact/internal/types/GenerateRandomBytes.go
- [x] lib/py/telepact/internal/generation/GenerateRandomFn.py → lib/go/telepact/internal/types/GenerateRandomFn.go
- [x] lib/py/telepact/internal/generation/GenerateRandomInteger.py → lib/go/telepact/internal/types/GenerateRandomInteger.go
- [x] lib/py/telepact/internal/generation/GenerateRandomMockCall.py → lib/go/telepact/internal/types/GenerateRandomMockCall.go
- [x] lib/py/telepact/internal/generation/GenerateRandomMockStub.py → lib/go/telepact/internal/types/GenerateRandomMockStub.go
- [x] lib/py/telepact/internal/generation/GenerateRandomNumber.py → lib/go/telepact/internal/types/GenerateRandomNumber.go
- [x] lib/py/telepact/internal/generation/GenerateRandomObject.py → lib/go/telepact/internal/types/GenerateRandomObject.go
- [x] lib/py/telepact/internal/generation/GenerateRandomSelect.py → lib/go/telepact/internal/types/GenerateRandomSelect.go
- [x] lib/py/telepact/internal/generation/GenerateRandomString.py → lib/go/telepact/internal/types/GenerateRandomString.go
- [x] lib/py/telepact/internal/generation/GenerateRandomStruct.py → lib/go/telepact/internal/types/GenerateRandomStruct.go
- [x] lib/py/telepact/internal/generation/GenerateRandomUnion.py → lib/go/telepact/internal/types/GenerateRandomUnion.go
- [x] lib/py/telepact/internal/generation/GenerateRandomValueOfType.py → lib/go/telepact/internal/types/GenerateRandomValueOfType.go
- [x] lib/py/telepact/internal/mock/IsSubMap.py → lib/go/telepact/internal/mock/IsSubMap.go
- [x] lib/py/telepact/internal/mock/IsSubMapEntryEqual.py → lib/go/telepact/internal/mock/IsSubMapEntryEqual.go
- [ ] lib/py/telepact/internal/mock/MockHandle.py → lib/go/telepact/internal/mock/MockHandle.go
- [x] lib/py/telepact/internal/mock/MockInvocation.py → lib/go/telepact/internal/mock/MockInvocation.go
- [x] lib/py/telepact/internal/mock/MockStub.py → lib/go/telepact/internal/mock/MockStub.go
- [x] lib/py/telepact/internal/mock/PartiallyMatches.py → lib/go/telepact/internal/mock/PartiallyMatches.go
- [x] lib/py/telepact/internal/mock/Verify.py → lib/go/telepact/internal/mock/Verify.go
- [x] lib/py/telepact/internal/mock/VerifyNoMoreInteractions.py → lib/go/telepact/internal/mock/VerifyNoMoreInteractions.go
- [ ] lib/py/telepact/internal/schema/ApplyErrorToParsedTypes.py → lib/go/telepact/internal/schema/ApplyErrorToParsedTypes.go
- [ ] lib/py/telepact/internal/schema/CatchErrorCollisions.py → lib/go/telepact/internal/schema/CatchErrorCollisions.go
- [ ] lib/py/telepact/internal/schema/CatchHeaderCollisions.py → lib/go/telepact/internal/schema/CatchHeaderCollisions.go
- [ ] lib/py/telepact/internal/schema/CreateMockTelepactSchemaFromFileJsonMap.py → lib/go/telepact/internal/schema/CreateMockTelepactSchemaFromFileJsonMap.go
- [ ] lib/py/telepact/internal/schema/CreateTelepactSchemaFromFileJsonMap.py → lib/go/telepact/internal/schema/CreateTelepactSchemaFromFileJsonMap.go
- [ ] lib/py/telepact/internal/schema/DerivePossibleSelects.py → lib/go/telepact/internal/schema/DerivePossibleSelects.go
- [ ] lib/py/telepact/internal/schema/FindMatchingSchemaKey.py → lib/go/telepact/internal/schema/FindMatchingSchemaKey.go
- [ ] lib/py/telepact/internal/schema/FindSchemaKey.py → lib/go/telepact/internal/schema/FindSchemaKey.go
- [ ] lib/py/telepact/internal/schema/GetAuthTelepactJson.py → lib/go/telepact/internal/schema/GetAuthTelepactJson.go
- [ ] lib/py/telepact/internal/schema/GetInternalTelepactJson.py → lib/go/telepact/internal/schema/GetInternalTelepactJson.go
- [ ] lib/py/telepact/internal/schema/GetMockTelepactJson.py → lib/go/telepact/internal/schema/GetMockTelepactJson.go
- [ ] lib/py/telepact/internal/schema/GetOrParseType.py → lib/go/telepact/internal/schema/GetOrParseType.go
- [ ] lib/py/telepact/internal/schema/GetPathDocumentCoordinatesPseudoJson.py → lib/go/telepact/internal/schema/GetPathDocumentCoordinatesPseudoJson.go
- [ ] lib/py/telepact/internal/schema/GetSchemaFileMap.py → lib/go/telepact/internal/schema/GetSchemaFileMap.go
- [ ] lib/py/telepact/internal/schema/GetTypeUnexpectedParseFailure.py → lib/go/telepact/internal/schema/GetTypeUnexpectedParseFailure.go
- [ ] lib/py/telepact/internal/schema/MapSchemaParseFailuresToPseudoJson.py → lib/go/telepact/internal/schema/MapSchemaParseFailuresToPseudoJson.go
- [ ] lib/py/telepact/internal/schema/ParseContext.py → lib/go/telepact/internal/schema/ParseContext.go
- [ ] lib/py/telepact/internal/schema/ParseErrorType.py → lib/go/telepact/internal/schema/ParseErrorType.go
- [ ] lib/py/telepact/internal/schema/ParseField.py → lib/go/telepact/internal/schema/ParseField.go
- [ ] lib/py/telepact/internal/schema/ParseFunctionType.py → lib/go/telepact/internal/schema/ParseFunctionType.go
- [ ] lib/py/telepact/internal/schema/ParseHeadersType.py → lib/go/telepact/internal/schema/ParseHeadersType.go
- [ ] lib/py/telepact/internal/schema/ParseStructFields.py → lib/go/telepact/internal/schema/ParseStructFields.go
- [ ] lib/py/telepact/internal/schema/ParseStructType.py → lib/go/telepact/internal/schema/ParseStructType.go
- [ ] lib/py/telepact/internal/schema/ParseTelepactSchema.py → lib/go/telepact/internal/schema/ParseTelepactSchema.go
- [ ] lib/py/telepact/internal/schema/ParseTypeDeclaration.py → lib/go/telepact/internal/schema/ParseTypeDeclaration.go
- [ ] lib/py/telepact/internal/schema/ParseUnionType.py → lib/go/telepact/internal/schema/ParseUnionType.go
- [ ] lib/py/telepact/internal/schema/SchemaParseFailure.py → lib/go/telepact/internal/schema/SchemaParseFailure.go

### Internal Types

- [x] lib/py/telepact/internal/types/GetType.py → lib/go/telepact/internal/types/GetType.go
- [x] lib/py/telepact/internal/types/TAny.py → lib/go/telepact/internal/types/TAny.go
- [x] lib/py/telepact/internal/types/TArray.py → lib/go/telepact/internal/types/TArray.go
- [x] lib/py/telepact/internal/types/TBoolean.py → lib/go/telepact/internal/types/TBoolean.go
- [x] lib/py/telepact/internal/types/TBytes.py → lib/go/telepact/internal/types/TBytes.go
- [x] lib/py/telepact/internal/types/TError.py → lib/go/telepact/internal/types/TError.go
- [x] lib/py/telepact/internal/types/TFieldDeclaration.py → lib/go/telepact/internal/types/TFieldDeclaration.go
- [x] lib/py/telepact/internal/types/THeaders.py → lib/go/telepact/internal/types/THeaders.go
- [x] lib/py/telepact/internal/types/TInteger.py → lib/go/telepact/internal/types/TInteger.go
- [x] lib/py/telepact/internal/types/TMockCall.py → lib/go/telepact/internal/types/TMockCall.go
- [x] lib/py/telepact/internal/types/TMockStub.py → lib/go/telepact/internal/types/TMockStub.go
- [x] lib/py/telepact/internal/types/TNumber.py → lib/go/telepact/internal/types/TNumber.go
- [x] lib/py/telepact/internal/types/TObject.py → lib/go/telepact/internal/types/TObject.go
- [x] lib/py/telepact/internal/types/TSelect.py → lib/go/telepact/internal/types/TSelect.go
- [x] lib/py/telepact/internal/types/TString.py → lib/go/telepact/internal/types/TString.go
- [x] lib/py/telepact/internal/types/TStruct.py → lib/go/telepact/internal/types/TStruct.go
- [x] lib/py/telepact/internal/types/TType.py → lib/go/telepact/internal/types/TType.go
- [x] lib/py/telepact/internal/types/TTypeDeclaration.py → lib/go/telepact/internal/types/TTypeDeclaration.go
- [x] lib/py/telepact/internal/types/TUnion.py → lib/go/telepact/internal/types/TUnion.go

### Validation & Error Helpers

- [x] lib/py/telepact/internal/validation/GetInvalidErrorMessage.py → lib/go/telepact/internal/validation/GetInvalidErrorMessage.go
- [x] lib/py/telepact/internal/validation/GetTypeUnexpectedValidationFailure.py → lib/go/telepact/internal/types/ValidationHelpers.go
- [x] lib/py/telepact/internal/validation/InvalidMessage.py → lib/go/telepact/internal/types/InvalidMessage.go
- [x] lib/py/telepact/internal/validation/InvalidMessageBody.py → lib/go/telepact/internal/types/InvalidMessageBody.go
- [x] lib/py/telepact/internal/validation/MapValidationFailuresToInvalidFieldCases.py → lib/go/telepact/internal/types/ValidationMapping.go
- [x] lib/py/telepact/internal/validation/ValidateArray.py → lib/go/telepact/internal/types/ValidationPrimitives.go
- [x] lib/py/telepact/internal/validation/ValidateBoolean.py → lib/go/telepact/internal/types/ValidationPrimitives.go
- [x] lib/py/telepact/internal/validation/ValidateBytes.py → lib/go/telepact/internal/types/ValidationPrimitives.go
- [x] lib/py/telepact/internal/validation/ValidateContext.py → lib/go/telepact/internal/types/ValidateContext.go
- [x] lib/py/telepact/internal/validation/ValidateHeaders.py → lib/go/telepact/internal/types/ValidationHeaders.go
- [x] lib/py/telepact/internal/validation/ValidateInteger.py → lib/go/telepact/internal/types/ValidationPrimitives.go
- [x] lib/py/telepact/internal/validation/ValidateMockCall.py → lib/go/telepact/internal/types/ValidationMock.go
- [x] lib/py/telepact/internal/validation/ValidateMockStub.py → lib/go/telepact/internal/types/ValidationMock.go
- [x] lib/py/telepact/internal/validation/ValidateNumber.py → lib/go/telepact/internal/types/ValidationPrimitives.go
- [x] lib/py/telepact/internal/validation/ValidateObject.py → lib/go/telepact/internal/types/ValidationPrimitives.go
- [x] lib/py/telepact/internal/validation/ValidateResult.py → lib/go/telepact/internal/validation/ValidateResult.go
- [x] lib/py/telepact/internal/validation/ValidateSelect.py → lib/go/telepact/internal/types/ValidationStruct.go
- [x] lib/py/telepact/internal/validation/ValidateString.py → lib/go/telepact/internal/types/ValidationPrimitives.go
- [x] lib/py/telepact/internal/validation/ValidateStruct.py → lib/go/telepact/internal/types/ValidationStruct.go
- [x] lib/py/telepact/internal/validation/ValidateStructFields.py → lib/go/telepact/internal/types/ValidationStruct.go (helper `validateStructFields`)
- [x] lib/py/telepact/internal/validation/ValidateUnion.py → lib/go/telepact/internal/types/ValidationStruct.go
- [x] lib/py/telepact/internal/validation/ValidateUnionStruct.py → lib/go/telepact/internal/types/ValidationStruct.go (helper `validateUnionStruct` logic)
- [x] lib/py/telepact/internal/validation/ValidateUnionTags.py → lib/go/telepact/internal/types/ValidationStruct.go (helper `validateUnionTags`)
- [x] lib/py/telepact/internal/validation/ValidateValueOfType.py → lib/go/telepact/internal/types/ValidationPrimitives.go
- [x] lib/py/telepact/internal/validation/ValidationFailure.py → lib/go/telepact/internal/types/ValidationFailure.go
