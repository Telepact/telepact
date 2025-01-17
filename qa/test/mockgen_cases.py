cases = {
    'simple': [
        [[{}, {'fn.setRandomSeed_': {'seed': 4}}], [{}, {'Ok_': {}}]],
        [[{}, {'fn.clearStubs_': {}}], [{}, {'Ok_': {}}]],
        [[{}, {'fn.clearCalls_': {}}], [{}, {'Ok_': {}}]],
        [[{}, {'fn.test': {}}], [{}, {'ErrorNoMatchingStub_': {}}]],
        [[{}, {'fn.createStub_': {'stub': {'fn.test': {}, '->': {'Ok_': {}}}}}], [{}, {'Ok_': {}}]],
        [[{}, {'fn.test': {}}], [{}, {'Ok_': {'createStub': {'fn.createStub_': {'stub': {'fn.example': {'arg1': 'AMIAxg'}, '->': {'Ok_': {'result': [140644391]}}}}}, 'data': {'field1': 'DMCYpA', 'field2': 424973015}, 'genericData': {'One': {'field1A': 'OjuM+A', 'field1B': 1872741801}}, 'select': {'->': {'Ok_': ['createStub']}}, 'verify': {'fn.verify_': {'call': {'fn.test': {}}}}}}]],
        [[{}, {'fn.test': {}}], [{}, {'Ok_': {'createStub': {'fn.createStub_': {'stub': {'fn.example': {'arg1': 'KqWwfw'}, '->': {'Ok_': {'result': [211679928]}}}}}, 'data': {'field1': True, 'field2': 1877592351}, 'genericData': {'One': {'field1A': 855520479, 'field1B': 1139797977}}, 'select': {'struct.Data': []}, 'verify': {'fn.verify_': {'call': {'fn.example': {'arg1': 'SPzH0Q'}}}}}}]],
        [[{}, {'fn.test': {}}], [{}, {'Ok_': {'createStub': {'fn.createStub_': {'stub': {'fn.test': {}, '->': {'Ok_': {'createStub': {'fn.createStub_': {'stub': {'fn.example': {'arg1': 'PielbA'}, '->': {'Ok_': {'result': [714464785]}}}}}, 'data': {'field1': 'BNr/2Q', 'field2': 446655334}, 'genericData': {'One': {'field1A': 'JJ/QjA', 'field1B': 1984367670}}, 'select': {'union.GenericData': {'Two': []}}, 'verify': {'fn.verify_': {'call': {'fn.test': {}}}}}}}}}, 'data': {'field1': True, 'field2': 118572919}, 'genericData': {'One': {'field1A': 1245329205, 'field1B': 1558334643}}, 'select': {'->': {'Ok_': ['data', 'genericData', 'select', 'verify']}, 'struct.Data': []}, 'verify': {'fn.verify_': {'call': {'fn.example': {'arg1': 'Hgeqiw'}}}}}}]],
    ],
}
