from msgpack import ExtType

cases = {
    'binary': [
        [[{'bin_': []}, {'fn.ping_': {}}], [{'enc_': {'Any': 0, 'Array': 1, 'BinaryDecodeFailure': 2, 'Boolean': 3, 'ErrorInvalidRequestBody_': 4, 'ErrorInvalidRequestHeaders_': 5, 'ErrorInvalidResponseBody_': 6, 'ErrorInvalidResponseHeaders_': 7, 'ErrorParseFailure_': 8, 'ErrorUnknown_': 9, 'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': 10, 'ExpectedJsonArrayOfTwoObjects': 11, 'ExtensionValidationFailed': 12, 'FunctionUnknown': 13, 'IncompatibleBinaryEncoding': 14, 'Integer': 15, 'JsonInvalid': 16, 'Null': 17, 'NullDisallowed': 18, 'Number': 19, 'NumberOutOfRange': 20, 'Object': 21, 'ObjectKeyDisallowed': 22, 'ObjectKeyRegexMatchCountUnexpected': 23, 'ObjectSizeUnexpected': 24, 'Ok_': 25, 'RequiredObjectKeyMissing': 26, 'String': 27, 'TypeUnexpected': 28, 'Unknown': 29, '_ext.Select_': 30, 'actual': 31, 'api': 32, 'cases': 33, 'data': 34, 'data!': 35, 'expected': 36, 'fn.api_': 37, 'fn.example': 38, 'fn.ping_': 39, 'id': 40, 'keys': 41, 'name': 42, 'path': 43, 'reason': 44, 'reasons': 45, 'regex': 46, 'struct.Data': 47, 'struct.ValidationFailure_': 48, 'union.ParseFailure_': 49, 'union.Type_': 50, 'union.ValidationFailureReason_': 51}, 'bin_': [-2135686103]}, {25: {}}]],
        [[{'msgpack': True, 'bin_': [0]}, {0: {}}], [{}, {'ErrorParseFailure_': {'reasons': [{'IncompatibleBinaryEncoding': {}}]}}]],
        [[{'msgpack': True, 'bin_': [-2135686103]}, {39: {}}], [{'bin_': [-2135686103]}, {25: {}}]],
        [[{'msgpack': True, 'bin_': [-2135686103], 'pac_': True, 'Ok_': {'data': [{'id': 1, 'name': 'one'}, {'id': 2, 'name': 'two'}]}}, {38: {}}], [{'bin_': [-2135686103], 'pac_': True}, {25: {34: [ExtType(17, b''), [None, 40, 42], [1, 'one'], [2, 'two']]}}]],
        [[{'msgpack': True, 'bin_': [-2135686103]}, {255: {}}], [{}, {'ErrorParseFailure_': {'reasons': [{'BinaryDecodeFailure': {}}]}}]],
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
