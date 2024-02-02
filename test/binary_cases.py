from msgpack import ExtType

cases = {
    'binary': [
        #[[{'_bin': []}, {'fn._ping': {}}], [{}, {'Ok': {}}]],
        [[{'msgpack': True, '_bin': [0]}, {0: {}}], [{}, {'_ErrorParseFailure': {'reasons': [{'IncompatibleBinaryEncoding': {}}]}}]],
        [[{'msgpack': True, '_bin': [383501484]}, {38: {}}], [{'_bin': [383501484]}, {19: {}}]],
        [[{'msgpack': True, '_bin': [383501484], '_pac': True, 'Ok': {'data': [{'id': 1, 'name': 'one'}, {'id': 2, 'name': 'two'}]}}, {40: {}}], [{'_bin': [383501484], '_pac': True}, {19: {34: [ExtType(17, b''), [None, 41, 42], [1, 'one'], [2, 'two']]}}]],
        [[{'msgpack': True, '_bin': [383501484]}, {255: {}}], [{}, {'_ErrorParseFailure': {'reasons': [{'BinaryDecodeFailure': {}}]}}]],
        #[b'false', [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        #['1337', [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}}]}}]],
        #['""', [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        #['{}', [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [[{}, {}], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}}]}}]],
        [[{}], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [[{}, {}, {}], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [[{}, {'Ok': 'wrong'}], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}}]}}]],
        #[[False, {'fn._ping': {}}], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        #[[0, {'fn._ping': {}}], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        #[['', {'fn._ping': {}}], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        #[[[], {'fn._ping': {}}], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [[{}, False], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [[{}, 0], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [[{}, ''], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [[{}, []], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
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
