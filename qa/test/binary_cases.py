from msgpack import ExtType

cases = {
    'binary': [
        [[{'bin_': []}, {'fn.ping_': {}}], [{'bin_': [1398405044], 'enc_': {'fn.example': 40, 'reason': 47, 'Null': 19, 'data': 36, 'String': 29, 'message!': 44, 'union.ValidationFailureReason_': 55, 'path': 46, 'struct.ValidationFailure_': 52, 'Unknown': 31, 'data!': 37, '_ext.Select_': 32, 'api': 34, 'id': 42, 'Boolean': 3, 'ErrorUnauthenticated_': 9, 'actual': 33, 'struct.Auth_': 50, 'expected': 38, 'NullDisallowed': 20, 'ObjectSizeUnexpected': 26, 'regex': 49, 'ExpectedJsonArrayOfTwoObjects': 13, 'name': 45, 'ExtensionValidationFailed': 14, 'Object': 23, 'union.ParseFailure_': 53, 'JsonInvalid': 18, 'ObjectKeyRegexMatchCountUnexpected': 25, 'ErrorUnknown_': 11, 'NumberOutOfRange': 22, 'reasons': 48, 'keys': 43, 'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': 12, 'struct.Data': 51, 'ErrorInvalidResponseHeaders_': 7, 'Any': 0, 'fn.api_': 39, 'IncompatibleBinaryEncoding': 16, 'Number': 21, 'BinaryDecodeFailure': 2, 'ErrorUnauthorized_': 10, 'ObjectKeyDisallowed': 24, 'TypeUnexpected': 30, 'ErrorInvalidRequestHeaders_': 5, 'Ok_': 27, 'ErrorInvalidRequestBody_': 4, 'cases': 35, 'union.Type_': 54, 'ErrorParseFailure_': 8, 'Array': 1, 'ErrorInvalidResponseBody_': 6, 'Integer': 17, 'RequiredObjectKeyMissing': 28, 'fn.ping_': 41, 'FunctionUnknown': 15}}, {27: {}}]],
        [[{'msgpack': True, 'bin_': [0]}, {0: {}}], [{}, {'ErrorParseFailure_': {'reasons': [{'IncompatibleBinaryEncoding': {}}]}}]],
        [[{'msgpack': True, 'bin_': [1398405044]}, {41: {}}], [{'bin_': [1398405044]}, {27: {}}]],
        [[{'msgpack': True, 'bin_': [1398405044], '_pac': True, 'Ok_': {'data': [{'id': 1, 'name': 'one'}, {'id': 2, 'name': 'two'}]}}, {40: {}}], [{'bin_': [1398405044], '_pac': True}, {27: {36: [ExtType(17, b''), [None, 42, 45], [1, 'one'], [2, 'two']]}}]],
        [[{'msgpack': True, 'bin_': [1398405044]}, {255: {}}], [{}, {'ErrorParseFailure_': {'reasons': [{'BinaryDecodeFailure': {}}]}}]],
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
