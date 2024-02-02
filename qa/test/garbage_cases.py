from msgpack import ExtType

cases = {
    'garbage': [
        [b'false', [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [b'0', [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [b'""', [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [b'[]', [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [b'{}', [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [[{}, {}], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}}]}}]],
        [[{}], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [[{}, {}, {}], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [[{}, {'Ok': 'wrong'}], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}}]}}]],
        [[False, {'fn._ping': {}}], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [[0, {'fn._ping': {}}], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [['', {'fn._ping': {}}], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [[[], {'fn._ping': {}}], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [[{}, False], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [[{}, 0], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [[{}, ''], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [[{}, []], [{}, {'_ErrorParseFailure': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]]
    ]
}
