from msgpack import ExtType

cases = {
    'binary': [
        [[{'bin_': []}, {'fn.ping_': {}}], [{'bin_': [1218031367], 'enc_': {'Any': 0, 'Array': 1, 'BinaryDecodeFailure': 2, 'Boolean': 3, 'ErrorInvalidRequestBody_': 4, 'ErrorInvalidRequestHeaders_': 5, 'ErrorInvalidResponseBody_': 6, 'ErrorInvalidResponseHeaders_': 7, 'ErrorParseFailure_': 8, 'ErrorUnauthenticated_': 9, 'ErrorUnauthorized_': 10, 'ErrorUnknown_': 11, 'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': 12, 'ExpectedJsonArrayOfTwoObjects': 13, 'ExtensionValidationFailed': 14, 'FunctionUnknown': 15, 'IncompatibleBinaryEncoding': 16, 'Integer': 17, 'JsonInvalid': 18, 'Null': 19, 'NullDisallowed': 20, 'Number': 21, 'NumberOutOfRange': 22, 'Object': 23, 'ObjectKeyDisallowed': 24, 'ObjectKeyRegexMatchCountUnexpected': 25, 'ObjectSizeUnexpected': 26, 'Ok_': 27, 'RequiredObjectKeyMissing': 28, 'String': 29, 'TypeUnexpected': 30, 'Unknown': 31, '_ext.Select_': 32, 'actual': 33, 'api': 34, 'cases': 35, 'data': 36, 'data!': 37, 'expected': 38, 'fn.api_': 39, 'fn.example': 40, 'fn.ping_': 41, 'id': 42, 'message!': 43, 'name': 44, 'path': 45, 'reason': 46, 'reasons': 47, 'regex': 48, 'struct.Auth_': 49, 'struct.Data': 50, 'struct.ValidationFailure_': 51, 'union.ParseFailure_': 52, 'union.Type_': 53, 'union.ValidationFailureReason_': 54}}, {27: {}}]],
        [[{'msgpack': True, 'bin_': [0]}, {0: {}}], [{}, {'ErrorParseFailure_': {'reasons': [{'IncompatibleBinaryEncoding': {}}]}}]],
        [[{'msgpack': True, 'bin_': [1218031367]}, {41: {}}], [{'bin_': [1218031367]}, {27: {}}]],
        [[{'msgpack': True, 'bin_': [1218031367], '_pac': True, 'Ok_': {'data': [{'id': 1, 'name': 'one'}, {'id': 2, 'name': 'two'}]}}, {40: {}}], [{'bin_': [1218031367], '_pac': True}, {27: {36: [ExtType(17, b''), [None, 42, 44], [1, 'one'], [2, 'two']]}}]],
        [[{'msgpack': True, 'bin_': [1218031367]}, {255: {}}], [{}, {'ErrorParseFailure_': {'reasons': [{'BinaryDecodeFailure': {}}]}}]],
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
