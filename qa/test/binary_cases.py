from msgpack import ExtType

cases = {
    'binary': [
        [[{'bin_': []}, {'fn.ping_': {}}], [{'enc_': {'Any': 0, 'Array': 1, 'ArrayElementDisallowed': 2, 'BinaryDecodeFailure': 3, 'Boolean': 4, 'ErrorInvalidRequestBody_': 5, 'ErrorInvalidRequestHeaders_': 6, 'ErrorInvalidResponseBody_': 7, 'ErrorInvalidResponseHeaders_': 8, 'ErrorParseFailure_': 9, 'ErrorUnknown_': 10, 'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': 11, 'ExpectedJsonArrayOfTwoObjects': 12, 'ExtensionValidationFailed': 13, 'FunctionUnknown': 14, 'IncompatibleBinaryEncoding': 15, 'Integer': 16, 'JsonInvalid': 17, 'Null': 18, 'NullDisallowed': 19, 'Number': 20, 'NumberOutOfRange': 21, 'Object': 22, 'ObjectKeyDisallowed': 23, 'ObjectKeyRegexMatchCountUnexpected': 24, 'ObjectSizeUnexpected': 25, 'Ok_': 26, 'RequiredObjectKeyMissing': 27, 'String': 28, 'TypeUnexpected': 29, 'Unknown': 30, '_ext.Select_': 31, 'actual': 32, 'api': 33, 'cases': 34, 'data': 35, 'data!': 36, 'expected': 37, 'fn.api_': 38, 'fn.example': 39, 'fn.ping_': 40, 'id': 41, 'key': 42, 'keys': 43, 'name': 44, 'path': 45, 'reason': 46, 'reasons': 47, 'regex': 48, 'struct.Data': 49, 'struct.ValidationFailure_': 50, 'union.ParseFailure_': 51, 'union.Type_': 52, 'union.ValidationFailureReason_': 53}, 'bin_': [-1563177148]}, {26: {}}]],
        [[{'msgpack': True, 'bin_': [0]}, {0: {}}], [{}, {'ErrorParseFailure_': {'reasons': [{'IncompatibleBinaryEncoding': {}}]}}]],
        [[{'msgpack': True, 'bin_': [-1563177148]}, {40: {}}], [{'bin_': [-1563177148]}, {26: {}}]],
        [[{'msgpack': True, 'bin_': [-1563177148], 'pac_': True, 'Ok_': {'data': [{'id': 1, 'name': 'one'}, {'id': 2, 'name': 'two'}]}}, {39: {}}], [{'bin_': [-1563177148], 'pac_': True}, {26: {35: [ExtType(17, b''), [None, 41, 44], [1, 'one'], [2, 'two']]}}]],
        [[{'msgpack': True, 'bin_': [-1563177148]}, {255: {}}], [{}, {'ErrorParseFailure_': {'reasons': [{'BinaryDecodeFailure': {}}]}}]],
        [[{'bin_': None}, {'fn.ping_': {}}], [{}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['bin_'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'bin_': False}, {'fn.ping_': {}}], [{}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['bin_'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'bin_': 0}, {'fn.ping_': {}}], [{}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['bin_'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'bin_': ''}, {'fn.ping_': {}}], [{}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['bin_'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'bin_': {}}, {'fn.ping_': {}}], [{}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['bin_'], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'bin_': [None]}, {'fn.ping_': {}}], [{}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['bin_', 0], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Integer': {}}}}}]}}]],
        [[{'bin_': [False]}, {'fn.ping_': {}}], [{}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['bin_', 0], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Integer': {}}}}}]}}]],
        [[{'bin_': [0.1]}, {'fn.ping_': {}}], [{}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['bin_', 0], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Integer': {}}}}}]}}]],
        [[{'bin_': ['']}, {'fn.ping_': {}}], [{}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['bin_', 0], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Integer': {}}}}}]}}]],
        [[{'bin_': [[]]}, {'fn.ping_': {}}], [{}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['bin_', 0], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Integer': {}}}}}]}}]],
        [[{'bin_': [{}]}, {'fn.ping_': {}}], [{}, {'ErrorInvalidRequestHeaders_': {'cases': [{'path': ['bin_', 0], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Integer': {}}}}}]}}]],
    ]
}

binary_client_rotation_cases = {
    'rotation': [
        [[{'Ok_': {}, '_toggleAlternateServer': True}, {'fn.test': {}}], [{'_assert': {'expectTwoRequests': True, 'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'Ok_': {}}]],
        [[{'Ok_': {}, '_toggleAlternateServer': True}, {'fn.test': {}}], [{'_assert': {'expectTwoRequests': True, 'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'Ok_': {}}]],
        [[{'Ok_': {}, '_toggleAlternateServer': True}, {'fn.test': {}}], [{'_assert': {'expectTwoRequests': True, 'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'Ok_': {}}]],
        [[{'Ok_': {}, '_toggleAlternateServer': True}, {'fn.test': {}}], [{'_assert': {'expectTwoRequests': True, 'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'Ok_': {}}]],
        [[{'Ok_': {}}, {'fn.test': {}}], [{'_assert': {'expectTwoRequests': True, 'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'Ok_': {}}]],
        [[{'Ok_': {}}, {'fn.test': {}}], [{'_assert': {'expectTwoRequests': True, 'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'Ok_': {}}]],
        [[{'Ok_': {}}, {'fn.test': {}}], [{'_assert': {'expectTwoRequests': True, 'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'Ok_': {}}]],
        [[{'Ok_': {}}, {'fn.test': {}}], [{}, {'Ok_': {}}]],
    ]
}
