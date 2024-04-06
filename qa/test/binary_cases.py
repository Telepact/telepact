from msgpack import ExtType

cases = {
    'binary': [
        [[{'bin_': []}, {'fn.ping_': {}}], [{'bin_': [504356281], 'enc_': {'Any': 0, 'Array': 1, 'BinaryDecodeFailure': 2, 'Boolean': 3, 'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': 4, 'ExpectedJsonArrayOfTwoObjects': 5, 'ExtensionValidationFailed': 6, 'FunctionUnknown': 7, 'IncompatibleBinaryEncoding': 8, 'Integer': 9, 'JsonInvalid': 10, 'Null': 11, 'NullDisallowed': 12, 'Number': 13, 'NumberOutOfRange': 14, 'Object': 15, 'ObjectKeyDisallowed': 16, 'ObjectKeyRegexMatchCountUnexpected': 17, 'ObjectSizeUnexpected': 18, 'Ok': 19, 'RequiredObjectKeyMissing': 20, 'String': 21, 'TypeUnexpected': 22, 'Unknown': 23, 'ErrorInvalidRequestBody_': 24, 'ErrorInvalidRequestHeaders_': 25, 'ErrorInvalidResponseBody_': 26, 'ErrorInvalidResponseHeaders_': 27, 'ErrorParseFailure_': 28, 'ErrorUnauthenticated_': 29, 'ErrorUnauthorized_': 30, 'ErrorUnknown_': 31, '_ext.Select_': 32, 'actual': 33, 'api': 34, 'cases': 35, 'data': 36, 'data!': 37, 'expected': 38, 'fn.api_': 39, 'fn.ping_': 40, 'fn.example': 41, 'id': 42, 'message!': 43, 'name': 44, 'path': 45, 'reason': 46, 'reasons': 47, 'regex': 48, 'struct.Data': 49, 'struct.Auth_': 50, 'struct._ValidationFailure': 51, 'union.ParseFailure_': 52, 'union.Type_': 53, 'union.ValidationFailureReason_': 54}}, {19: {}}]],
        [[{'msgpack': True, 'bin_': [0]}, {0: {}}], [{}, {'ErrorParseFailure_': {'reasons': [{'IncompatibleBinaryEncoding': {}}]}}]],
        [[{'msgpack': True, 'bin_': [504356281]}, {40: {}}], [{'bin_': [504356281]}, {19: {}}]],
        [[{'msgpack': True, 'bin_': [504356281], '_pac': True, 'Ok': {'data': [{'id': 1, 'name': 'one'}, {'id': 2, 'name': 'two'}]}}, {41: {}}], [{'bin_': [504356281], '_pac': True}, {19: {36: [ExtType(17, b''), [None, 42, 44], [1, 'one'], [2, 'two']]}}]],
        [[{'msgpack': True, 'bin_': [504356281]}, {255: {}}], [{}, {'ErrorParseFailure_': {'reasons': [{'BinaryDecodeFailure': {}}]}}]],
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
        [[{'Ok': {}, '_toggleAlternateServer': True}, {'fn.test': {}}], [{'_assert': {'expectTwoRequests': True, 'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'Ok': {}}]],
        [[{'Ok': {}, '_toggleAlternateServer': True}, {'fn.test': {}}], [{'_assert': {'expectTwoRequests': True, 'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'Ok': {}}]],
        [[{'Ok': {}, '_toggleAlternateServer': True}, {'fn.test': {}}], [{'_assert': {'expectTwoRequests': True, 'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'Ok': {}}]],
        [[{'Ok': {}, '_toggleAlternateServer': True}, {'fn.test': {}}], [{'_assert': {'expectTwoRequests': True, 'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'Ok': {}}]],
        [[{'Ok': {}}, {'fn.test': {}}], [{'_assert': {'expectTwoRequests': True, 'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'Ok': {}}]],
        [[{'Ok': {}}, {'fn.test': {}}], [{'_assert': {'expectTwoRequests': True, 'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'Ok': {}}]],
        [[{'Ok': {}}, {'fn.test': {}}], [{'_assert': {'expectTwoRequests': True, 'skipBinaryCheck': True, 'skipFieldIdCheck': True}}, {'Ok': {}}]],
        [[{'Ok': {}}, {'fn.test': {}}], [{}, {'Ok': {}}]],
    ]
}
