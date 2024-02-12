from msgpack import ExtType

cases = {
    'binary': [
        [[{'_bin': []}, {'fn._ping': {}}], [{'_bin': [383501484], '_enc': {'fn.example': 40, 'reason': 44, 'Null': 11, 'data': 34, '_ErrorInvalidResponseBody': 28, 'String': 21, 'path': 43, 'Unknown': 25, 'data!': 35, 'api': 32, 'id': 41, 'Boolean': 3, '_ErrorUnknown': 30, 'UnionCaseUnknown': 24, 'actual': 31, 'expected': 36, 'NullDisallowed': 12, 'ObjectSizeUnexpected': 18, 'regex': 46, 'ExpectedJsonArrayOfTwoObjects': 5, 'fn._ping': 38, 'name': 42, 'ExtensionValidationFailed': 6, 'Object': 15, 'JsonInvalid': 10, 'ObjectKeyRegexMatchCountUnexpected': 17, 'union._BodyValidationFailureReason': 50, 'NumberOutOfRange': 14, 'reasons': 45, '_ErrorInvalidRequestHeaders': 27, 'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': 4, 'struct.Data': 47, 'Any': 0, 'union._Type': 53, 'struct._HeaderValidationFailure': 49, 'IncompatibleBinaryEncoding': 8, 'Number': 13, 'union._ParseFailure': 52, 'TypeUnknown': 23, 'BinaryDecodeFailure': 2, 'union._HeaderValidationFailureReason': 51, 'ObjectKeyDisallowed': 16, 'TypeUnexpected': 22, '_ErrorParseFailure': 29, '_ErrorInvalidRequestBody': 26, 'cases': 33, 'fn._api': 37, 'Array': 1, 'Integer': 9, 'RequiredObjectKeyMissing': 20, 'struct._BodyValidationFailure': 48, 'FunctionUnknown': 7, 'Ok': 19, 'fn._unknown': 39}}, {19: {}}]],
        [[{'msgpack': True, '_bin': [0]}, {0: {}}], [{}, {'_ErrorParseFailure': {'reasons': [{'IncompatibleBinaryEncoding': {}}]}}]],
        [[{'msgpack': True, '_bin': [383501484]}, {38: {}}], [{'_bin': [383501484]}, {19: {}}]],
        [[{'msgpack': True, '_bin': [383501484], '_pac': True, 'Ok': {'data': [{'id': 1, 'name': 'one'}, {'id': 2, 'name': 'two'}]}}, {40: {}}], [{'_bin': [383501484], '_pac': True}, {19: {34: [ExtType(17, b''), [None, 41, 42], [1, 'one'], [2, 'two']]}}]],
        [[{'msgpack': True, '_bin': [383501484]}, {255: {}}], [{}, {'_ErrorParseFailure': {'reasons': [{'BinaryDecodeFailure': {}}]}}]],
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
