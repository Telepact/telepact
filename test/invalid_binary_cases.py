cases = {
    'binary': [
        ['\x92\x81\xA4_bin\x91\xd2\x00\x00\x00\x00\x81\x00\x80', [{}, {'_errorParseFailure': {'reasons': ['IncompatibleBinaryEncoding']}}]],
        ['\x80', [{}, {'_errorParseFailure': {'reasons': ['InvalidJson']}}]],
        ['\x92\x81\xA4_bin\x91\xd2vz\'\x17\x81!\x80','\x92\x81\xa4_bin\x91\xcevz\'\x17\x81%\x80'],
        ['\x92\x81\xA4_bin\x91\xd2vz\'\x17\x81\x7f\x80', [{}, {'_errorParseFailure': {'reasons': ['BinaryDecodeFailure']}}]],
        ['false', [{}, {'_errorParseFailure': {'reasons': ['MessageMustBeArrayWithTwoElements']}}]],
        #['1337', [{}, {'_errorParseFailure': {'reasons': ['MessageMustBeArrayWithTwoElements']}}]],
        ['""', [{}, {'_errorParseFailure': {'reasons': ['MessageMustBeArrayWithTwoElements']}}]],
        ['{}', [{}, {'_errorParseFailure': {'reasons': ['MessageMustBeArrayWithTwoElements']}}]],
        [[{}, {}], [{}, {'_errorParseFailure': {'reasons': ['BodyMustBeUnionType']}}]],
        [[False, {'fn._ping': {}}], [{}, {'_errorParseFailure': {'reasons': ['HeadersMustBeObject']}}]],
        [[0, {'fn._ping': {}}], [{}, {'_errorParseFailure': {'reasons': ['HeadersMustBeObject']}}]],
        [['', {'fn._ping': {}}], [{}, {'_errorParseFailure': {'reasons': ['HeadersMustBeObject']}}]],
        [[[], {'fn._ping': {}}], [{}, {'_errorParseFailure': {'reasons': ['HeadersMustBeObject']}}]],
        [[{}, False], [{}, {'_errorParseFailure': {'reasons': ['BodyMustBeObject']}}]],
        [[{}, 0], [{}, {'_errorParseFailure': {'reasons': ['BodyMustBeObject']}}]],
        [[{}, ''], [{}, {'_errorParseFailure': {'reasons': ['BodyMustBeObject']}}]],
        [[{}, []], [{}, {'_errorParseFailure': {'reasons': ['BodyMustBeObject']}}]],
        [[{'_bin': False}, {'fn._ping': {}}], [{}, {'_errorInvalidRequestHeaders': {'cases': [{'path': 'headers{_bin}', 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'_bin': 0}, {'fn._ping': {}}], [{}, {'_errorInvalidRequestHeaders': {'cases': [{'path': 'headers{_bin}', 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'_bin': ''}, {'fn._ping': {}}], [{}, {'_errorInvalidRequestHeaders': {'cases': [{'path': 'headers{_bin}', 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'_bin': {}}, {'fn._ping': {}}], [{}, {'_errorInvalidRequestHeaders': {'cases': [{'path': 'headers{_bin}', 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{'_bin': [False]}, {'fn._ping': {}}], [{}, {'_errorInvalidRequestHeaders': {'cases': [{'path': 'headers{_bin}[0]', 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Integer': {}}}}}]}}]],
        [[{'_bin': [0.1]}, {'fn._ping': {}}], [{}, {'_errorInvalidRequestHeaders': {'cases': [{'path': 'headers{_bin}[0]', 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Integer': {}}}}}]}}]],
        [[{'_bin': ['']}, {'fn._ping': {}}], [{}, {'_errorInvalidRequestHeaders': {'cases': [{'path': 'headers{_bin}[0]', 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Integer': {}}}}}]}}]],
        [[{'_bin': [[]]}, {'fn._ping': {}}], [{}, {'_errorInvalidRequestHeaders': {'cases': [{'path': 'headers{_bin}[0]', 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Integer': {}}}}}]}}]],
        [[{'_bin': [{}]}, {'fn._ping': {}}], [{}, {'_errorInvalidRequestHeaders': {'cases': [{'path': 'headers{_bin}[0]', 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Integer': {}}}}}]}}]]
    ]
}

binary_client_rotation_cases = {
    'rotation': [
        [[{'ok': {}, '_toggleAlternateServer': True}, {'fn.test': {}}], [{}, {'ok': {}}], False],
        [[{'ok': {}, '_toggleAlternateServer': True}, {'fn.test': {}}], [{}, {'ok': {}}], False],
        [[{'ok': {}, '_toggleAlternateServer': True}, {'fn.test': {}}], [{}, {'ok': {}}], False],
        [[{'ok': {}, '_toggleAlternateServer': True}, {'fn.test': {}}], [{}, {'ok': {}}], False],
        [[{'ok': {}}, {'fn.test': {}}], [{}, {'ok': {}}], False],
        [[{'ok': {}}, {'fn.test': {}}], [{}, {'ok': {}}], False],
        [[{'ok': {}}, {'fn.test': {}}], [{}, {'ok': {}}], False],
        [[{'ok': {}}, {'fn.test': {}}], [{}, {'ok': {}}]],
    ]
}
