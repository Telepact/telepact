cases = {
    'binary': [
        ['\x92\x81\xA4_bin\x91\xd2\x00\x00\x00\x00\x81\x00\x80', [{}, {'_ErrorParseFailure': {'reasons': [{'IncompatibleBinaryEncoding': {}}]}}]],
        ['\x80', [{}, {'_ErrorParseFailure': {'reasons': [{'InvalidJson': {}}]}}]],
        ['\x92\x81\xA4_bin\x91\xd2\xc9t\xd9\xeb\x81(\x80','\x92\x81\xa4_bin\x91\xd2\xc9t\xd9\xeb\x81\x12\x80'],
        ['\x92\x81\xA4_bin\x91\xd2\xc9t\xd9\xeb\x81\x7f\x80', [{}, {'_ErrorParseFailure': {'reasons': [{'BinaryDecodeFailure': {}}]}}]],
        ['false', [{}, {'_ErrorParseFailure': {'reasons': [{'MessageMustBeArrayWithTwoElements': {}}]}}]],
        #['1337', [{}, {'_ErrorParseFailure': {'reasons': [{'MessageMustBeArrayWithTwoElements': {}}]}}]],
        ['""', [{}, {'_ErrorParseFailure': {'reasons': [{'MessageMustBeArrayWithTwoElements': {}}]}}]],
        ['{}', [{}, {'_ErrorParseFailure': {'reasons': [{'MessageMustBeArrayWithTwoElements': {}}]}}]],
        [[{}, {}], [{}, {'_ErrorParseFailure': {'reasons': [{'BodyMustBeUnionType': {}}]}}]],
        [[False, {'fn._ping': {}}], [{}, {'_ErrorParseFailure': {'reasons': [{'HeadersMustBeObject': {}}]}}]],
        [[0, {'fn._ping': {}}], [{}, {'_ErrorParseFailure': {'reasons': [{'HeadersMustBeObject': {}}]}}]],
        [['', {'fn._ping': {}}], [{}, {'_ErrorParseFailure': {'reasons': [{'HeadersMustBeObject': {}}]}}]],
        [[[], {'fn._ping': {}}], [{}, {'_ErrorParseFailure': {'reasons': [{'HeadersMustBeObject': {}}]}}]],
        [[{}, False], [{}, {'_ErrorParseFailure': {'reasons': [{'BodyMustBeObject': {}}]}}]],
        [[{}, 0], [{}, {'_ErrorParseFailure': {'reasons': [{'BodyMustBeObject': {}}]}}]],
        [[{}, ''], [{}, {'_ErrorParseFailure': {'reasons': [{'BodyMustBeObject': {}}]}}]],
        [[{}, []], [{}, {'_ErrorParseFailure': {'reasons': [{'BodyMustBeObject': {}}]}}]],
        [[{'_bin': False}, {'fn._ping': {}}], [{}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['headers', '_bin'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'_bin': 0}, {'fn._ping': {}}], [{}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['headers', '_bin'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'_bin': ''}, {'fn._ping': {}}], [{}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['headers', '_bin'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'_bin': {}}, {'fn._ping': {}}], [{}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['headers', '_bin'], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'_bin': [False]}, {'fn._ping': {}}], [{}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['headers', '_bin', 0], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Integer': {}}}}}]}}]],
        [[{'_bin': [0.1]}, {'fn._ping': {}}], [{}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['headers', '_bin', 0], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Integer': {}}}}}]}}]],
        [[{'_bin': ['']}, {'fn._ping': {}}], [{}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['headers', '_bin', 0], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Integer': {}}}}}]}}]],
        [[{'_bin': [[]]}, {'fn._ping': {}}], [{}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['headers', '_bin', 0], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Integer': {}}}}}]}}]],
        [[{'_bin': [{}]}, {'fn._ping': {}}], [{}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['headers', '_bin', 0], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Integer': {}}}}}]}}]]
    ]
}

binary_client_rotation_cases = {
    'rotation': [
        [[{'Ok': {}, '_toggleAlternateServer': True}, {'fn.test': {}}], [{}, {'Ok': {}}], False],
        [[{'Ok': {}, '_toggleAlternateServer': True}, {'fn.test': {}}], [{}, {'Ok': {}}], False],
        [[{'Ok': {}, '_toggleAlternateServer': True}, {'fn.test': {}}], [{}, {'Ok': {}}], False],
        [[{'Ok': {}, '_toggleAlternateServer': True}, {'fn.test': {}}], [{}, {'Ok': {}}], False],
        [[{'Ok': {}}, {'fn.test': {}}], [{}, {'Ok': {}}], False],
        [[{'Ok': {}}, {'fn.test': {}}], [{}, {'Ok': {}}], False],
        [[{'Ok': {}}, {'fn.test': {}}], [{}, {'Ok': {}}], False],
        [[{'Ok': {}}, {'fn.test': {}}], [{}, {'Ok': {}}]],
    ]
}
