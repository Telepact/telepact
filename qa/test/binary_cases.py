from msgpack import ExtType

cases = {
    'binary': [
        [[{'_bin': []}, {'fn._ping': {}}], [{'_bin': [1098979525], '_enc': {'Any': 0, 'Array': 1, 'BinaryDecodeFailure': 2, 'Boolean': 3, 'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': 4, 'ExpectedJsonArrayOfTwoObjects': 5, 'ExtensionValidationFailed': 6, 'FunctionUnknown': 7, 'IncompatibleBinaryEncoding': 8, 'Integer': 9, 'JsonInvalid': 10, 'Null': 11, 'NullDisallowed': 12, 'Number': 13, 'NumberOutOfRange': 14, 'Object': 15, 'ObjectKeyDisallowed': 16, 'ObjectKeyRegexMatchCountUnexpected': 17, 'ObjectSizeUnexpected': 18, 'Ok': 19, 'RequiredObjectKeyMissing': 20, 'String': 21, 'TypeUnexpected': 22, 'Unknown': 23, '_ErrorInvalidRequestBody': 24, '_ErrorInvalidRequestHeaders': 25, '_ErrorInvalidResponseBody': 26, '_ErrorInvalidResponseHeaders': 27, '_ErrorParseFailure': 28, '_ErrorUnauthenticated': 29, '_ErrorUnauthorized': 30, '_ErrorUnknown': 31, '_ext._Select': 32, 'actual': 33, 'api': 34, 'cases': 35, 'data': 36, 'data!': 37, 'expected': 38, 'fn._api': 39, 'fn._ping': 40, 'fn._unknown': 41, 'fn.example': 42, 'id': 43, 'message!': 44, 'name': 45, 'path': 46, 'reason': 47, 'reasons': 48, 'regex': 49, 'struct.Data': 50, 'struct._Auth': 51, 'struct._ValidationFailure': 52, 'union._ParseFailure': 53, 'union._Type': 54, 'union._ValidationFailureReason': 55}}, {19: {}}]],
        [[{'msgpack': True, '_bin': [0]}, {0: {}}], [{}, {'_ErrorParseFailure': {'reasons': [{'IncompatibleBinaryEncoding': {}}]}}]],
        [[{'msgpack': True, '_bin': [1098979525]}, {40: {}}], [{'_bin': [1098979525]}, {19: {}}]],
        [[{'msgpack': True, '_bin': [1098979525], '_pac': True, 'Ok': {'data': [{'id': 1, 'name': 'one'}, {'id': 2, 'name': 'two'}]}}, {42: {}}], [{'_bin': [1098979525], '_pac': True}, {19: {36: [ExtType(17, b''), [None, 43, 45], [1, 'one'], [2, 'two']]}}]],
        [[{'msgpack': True, '_bin': [1098979525]}, {255: {}}], [{}, {'_ErrorParseFailure': {'reasons': [{'BinaryDecodeFailure': {}}]}}]],
        [[{'_bin': None}, {'fn._ping': {}}], [{}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_bin'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'_bin': False}, {'fn._ping': {}}], [{}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_bin'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'_bin': 0}, {'fn._ping': {}}], [{}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_bin'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'_bin': ''}, {'fn._ping': {}}], [{}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_bin'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'_bin': {}}, {'fn._ping': {}}], [{}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_bin'], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'_bin': [None]}, {'fn._ping': {}}], [{}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_bin', 0], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Integer': {}}}}}]}}]],
        [[{'_bin': [False]}, {'fn._ping': {}}], [{}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_bin', 0], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Integer': {}}}}}]}}]],
        [[{'_bin': [0.1]}, {'fn._ping': {}}], [{}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_bin', 0], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Integer': {}}}}}]}}]],
        [[{'_bin': ['']}, {'fn._ping': {}}], [{}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_bin', 0], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Integer': {}}}}}]}}]],
        [[{'_bin': [[]]}, {'fn._ping': {}}], [{}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_bin', 0], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Integer': {}}}}}]}}]],
        [[{'_bin': [{}]}, {'fn._ping': {}}], [{}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_bin', 0], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Integer': {}}}}}]}}]],
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
