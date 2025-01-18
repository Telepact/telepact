cases = {
    'simple': [
        [[{}, {'fn.setRandomSeed_': {'seed': 4}}], [{}, {'Ok_': {}}]],
        [[{}, {'fn.clearStubs_': {}}], [{}, {'Ok_': {}}]],
        [[{}, {'fn.clearCalls_': {}}], [{}, {'Ok_': {}}]],
        [[{}, {'fn.test': {}}], [{}, {'ErrorNoMatchingStub_': {}}]],
        [[{}, {'fn.createStub_': {'stub': {'fn.test': {}, '->': {'Ok_': {}}}}}], [{}, {'Ok_': {}}]],
        [[{}, {'fn.test': {}}], [{}, {'Ok_': {'createStub': {'fn.createStub_': {'stub': {'fn.example': {}, '->': {'Ok_': {}}}}}, 'data': {'field1': 'EIUIJQ', 'field2': 213948580}, 'genericData': {'One': {'field1A': 1214536979, 'field1B': 976981240}}, 'select': {'->': {'Ok_': ['createStub', 'data']}}, 'verify': {'fn.verify_': {'call': {'fn.example': {'arg1': 'aR8f/A'}}}}}}]],
        [[{}, {'fn.test': {}}], [{}, {'Ok_': {'createStub': {'fn.createStub_': {'stub': {'fn.test': {}, '->': {'Ok_': {'createStub': {'fn.createStub_': {}}, 'data': {'field2': 2024861446}, 'genericData': {'One': {}}, 'select': {}}}}}}, 'data': {'field1': True, 'field2': 103563748}, 'genericData': {'One': {'field1A': 714464785, 'field1B': 1681104842}}, 'select': {'->': {'Ok_': []}, 'union.GenericData': {'Two': []}}, 'verify': {'fn.verify_': {'call': {'fn.test': {}}}}}}]],
        [[{}, {'fn.test': {}}], [{}, {'Ok_': {'createStub': {'fn.createStub_': {'stub': {'fn.test': {}, '->': {'Ok_': {'genericData': {'One': {'field1B': 440112602}}, 'verify': {'fn.verify_': {}}}}}}}, 'data': {'field1': 450617733, 'field2': 291553657}, 'genericData': {'One': {'field1A': False, 'field1B': 1469458004}}, 'select': {}, 'verify': {'fn.verify_': {'call': {'fn.test': {}}}}}}]],
    ],
}
