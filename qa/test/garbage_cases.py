from msgpack import ExtType

cases = {
    'garbage': [
        [b'false', [{}, {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [b'0', [{}, {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [b'""', [{}, {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [b'[]', [{}, {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [b'{}', [{}, {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [[{}, {}], [{}, {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}}]}}]],
        [[{}], [{}, {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [[{}, {}, {}], [{}, {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [[{}, {'Ok': 'wrong'}], [{}, {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject': {}}]}}]],
        [[False, {'fn.ping_': {}}], [{}, {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [[0, {'fn.ping_': {}}], [{}, {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [['', {'fn.ping_': {}}], [{}, {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [[[], {'fn.ping_': {}}], [{}, {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [[{}, False], [{}, {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [[{}, 0], [{}, {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [[{}, ''], [{}, {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]],
        [[{}, []], [{}, {'ErrorParseFailure_': {'reasons': [{'ExpectedJsonArrayOfTwoObjects': {}}]}}]]
    ]
}
