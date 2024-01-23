cases = {
    'binary': [
        [b'\x92\x81\xA4_bin\x91\xd2\x00\x00\x00\x00\x81\x00\x80', [{}, {'_ErrorParseFailure': {'reasons': [{'IncompatibleBinaryEncoding': {}}]}}]],
        [b'\x80', [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}}]}}]],
        [b'\x92\x81\xA4_bin\x91\xd2\xc9t\xd9\xeb\x81(\x80', b'\x92\x81\xa4_bin\x91\xd2\xc9t\xd9\xeb\x81\x12\x80'],
        [b'\x92\x81\xA4_bin\x91\xd2\xc9t\xd9\xeb\x81\x7f\x80', [{}, {'_ErrorParseFailure': {'reasons': [{'BinaryDecodeFailure': {}}]}}]],
        [b'false', [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}}]}}]],
        #['1337', [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}}]}}]],
        ['""', [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}}]}}]],
        ['{}', [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}}]}}]],
        [[{}, {}], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}}]}}]],
        [[{}], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}}]}}]],
        [[{}, {}, {}], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}}]}}]],
        [[{}, {'Ok': 'wrong'}], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}}]}}]],
        [[False, {'fn._ping': {}}], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}}]}}]],
        [[0, {'fn._ping': {}}], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}}]}}]],
        [['', {'fn._ping': {}}], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}}]}}]],
        [[[], {'fn._ping': {}}], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}}]}}]],
        [[{}, False], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}}]}}]],
        [[{}, 0], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}}]}}]],
        [[{}, ''], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}}]}}]],
        [[{}, []], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}}]}}]],
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
        [[{'_bin': [{}]}, {'fn._ping': {}}], [{}, {'_ErrorInvalidRequestHeaders': {'cases': [{'path': ['_bin', 0], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Integer': {}}}}}]}}]]
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
