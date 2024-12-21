cases = {
    'schema': [
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Example': {}}, {'struct.Example': {}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [1, 'struct.Example'], 'reason': {'PathCollision': {'document': 'auto_', 'path': [0, 'struct.Example']}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Example': {'field': ['boolean'], 'field!': ['integer']}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'struct.Example', 'field!'], 'reason': {'PathCollision': {'document': 'auto_', 'path': [0, 'struct.Example', 'field']}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Example': {'field!': ['boolean'], 'field': ['integer']}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'struct.Example', 'field'], 'reason': {'PathCollision': {'document': 'auto_', 'path': [0, 'struct.Example', 'field!']}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'invalid.Example': {}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0], 'reason': {'ObjectKeyRegexMatchCountUnexpected': {'regex': '^(((fn|errors|requestHeader|responseHeader|info)|((struct|union|_ext)(<[0-2]>)?))\\..*)', 'actual': 0, 'expected': 1, 'keys': ['invalid.Example']}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': None}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': False}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': 0}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': ''}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': {}}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.example': {},'->': [{'Ok_': {}},{"Err": {}}]},{'errors.Broken': [{'Err': {}}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [1, 'errors.Broken', 0, 'Err'], 'reason': {'PathCollision': {'document': 'auto_', 'path': [0, '->', 1, 'Err']}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'errors.Broken': []}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'errors.Broken'], 'reason': {'EmptyArrayDisallowed': {}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'errors.Broken': [{"Err": {}}]}, {'errors.Other': [{'Err': {}}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'errors.Other', 'document': 'auto_', 'path': [1, 'errors.Other', 0, 'Err'], 'reason': {'PathCollision': {'document': 'auto_', 'path': [0, 'errors.Broken', 0, 'Err']}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'errors.Broken': [{'Err': {}}], 'unknown': False}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'unknown'], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'errors.Broken': [{'Err': {}, 'Unknown': {}}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'errors.Broken', 0], 'reason': {'ObjectKeyRegexMatchCountUnexpected': {'actual': 2, 'expected': 1, 'regex': '^([A-Z][a-zA-Z0-9_]*)$', 'keys': ['Err', 'Unknown']}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'errors.Broken': [{'wrong': {}}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'errors.Broken', 0], 'reason': {'ObjectKeyRegexMatchCountUnexpected': {'actual': 0, 'expected': 1, 'regex': '^([A-Z][a-zA-Z0-9_]*)$', 'keys': ['wrong']}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'errors.Broken': [{}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'errors.Broken', 0], 'reason': {'ObjectKeyRegexMatchCountUnexpected': {'actual': 0, 'expected': 1, 'regex': '^([A-Z][a-zA-Z0-9_]*)$', 'keys': []}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'errors.Broken': [None]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'errors.Broken', 0], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'errors.Broken': [False]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'errors.Broken', 0], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'errors.Broken': [0]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'errors.Broken', 0], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'errors.Broken': ['']}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'errors.Broken', 0], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'errors.Broken': [[]]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'errors.Broken', 0], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Broken': None}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'struct.Broken'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Broken': False}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'struct.Broken'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Broken': 0}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'struct.Broken'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Broken': ''}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'struct.Broken'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Broken': []}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'struct.Broken'], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Example': {'@invalid': []}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'struct.Example', '@invalid'], 'reason': {'KeyRegexMatchFailed': {'regex': '^([a-z][a-zA-Z0-9_]*)(!)?$'}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Example': {'field': []}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'struct.Example', 'field'], 'reason': {'EmptyArrayDisallowed': {}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Example': {'field': [None]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'struct.Example', 'field', 0], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Example': {'field': [False]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'struct.Example', 'field', 0], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Example': {'field': [0]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'struct.Example', 'field', 0], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Example': {'field': [[]]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'struct.Example', 'field', 0], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Example': {'field': [{}]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'struct.Example', 'field', 0], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Example': {'field': ['']}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'struct.Example', 'field', 0], 'reason': {'StringRegexMatchFailed': {'regex': '^(.+?)(\\?)?$'}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct<1>.Example': {'field': ['T0?']}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'struct<1>.Example', 'document': 'auto_', 'path': [0, 'struct<1>.Example', 'field', 0], 'reason': {'StringRegexMatchFailed': {'regex': '^(.+?)[^\\?]$'}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct<1>.Param': {'field': ['T0']},'struct.Example': {'field': ['struct<1>.Param']}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0], 'reason': {'ObjectKeyRegexMatchCountUnexpected': {'regex': '^(((fn|errors|requestHeader|responseHeader|info)|((struct|union|_ext)(<[0-2]>)?))\\..*)', 'actual': 2, 'expected': 1, 'keys': ['struct.Example', 'struct<1>.Param']}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct<1>.Param': {'field': ['T0']},},{'struct.Example': {'field': ['struct<1>.Param']}}]}}],[{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [1, 'struct.Example', 'field'], 'reason': {'ArrayLengthUnexpected': {'actual': 1, 'expected': 2}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct<1>.Param': {'field': ['T0']},},{'struct.Example': {'field': ['struct<1>.Param', None]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [1, 'struct.Example', 'field', 1], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct<1>.Param': {'field': ['T0']},},{'struct.Example': {'field': ['struct<1>.Param', False]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [1, 'struct.Example', 'field', 1], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct<1>.Param': {'field': ['T0']},},{'struct.Example': {'field': ['struct<1>.Param', 0]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [1, 'struct.Example', 'field', 1], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct<1>.Param': {'field': ['T0']},},{'struct.Example': {'field': ['struct<1>.Param', '']}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [1, 'struct.Example', 'field', 1], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct<1>.Param': {'field': ['T0']},},{'struct.Example': {'field': ['struct<1>.Param', {}]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [1, 'struct.Example', 'field', 1], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct<1>.Param': {'field': ['T0']},},{'struct.Example': {'field': ['struct<1>.Param', [None]]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [1, 'struct.Example', 'field', 1, 0], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct<1>.Param': {'field': ['T0']},},{'struct.Example': {'field': ['struct<1>.Param', [False]]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [1, 'struct.Example', 'field', 1, 0], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct<1>.Param': {'field': ['T0']},},{'struct.Example': {'field': ['struct<1>.Param', [0]]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [1, 'struct.Example', 'field', 1, 0], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct<1>.Param': {'field': ['T0']},},{'struct.Example': {'field': ['struct<1>.Param', [[]]]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [1, 'struct.Example', 'field', 1, 0], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct<1>.Param': {'field': ['T0']},},{'struct.Example': {'field': ['struct<1>.Param', [{}]]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [1, 'struct.Example', 'field', 1, 0], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Example': {'field': ['struct.Broken']},},{'struct.Example2': {'field': ['struct.Broken']},},{'struct.Broken': {'field': [None]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [2, 'struct.Broken', 'field', 0], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Example': {'field': ['struct.Broken']},},{'struct.Example2': {'field': ['struct.Broken']},},{'struct.Broken': {'field': [False]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [2, 'struct.Broken', 'field', 0], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Example': {'field': ['struct.Broken']},},{'struct.Example2': {'field': ['struct.Broken']},},{'struct.Broken': {'field': [0]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [2, 'struct.Broken', 'field', 0], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Example': {'field': ['struct.Broken']},},{'struct.Example2': {'field': ['struct.Broken']},},{'struct.Broken': {'field': [[]]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [2, 'struct.Broken', 'field', 0], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Example': {'field': ['struct.Broken']},},{'struct.Example2': {'field': ['struct.Broken']},},{'struct.Broken': {'field': [{}]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [2, 'struct.Broken', 'field', 0], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Broken': {'field': ['wrong']},},]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'struct.Broken', 'field', 0], 'reason': {'StringRegexMatchFailed': {'regex': '^(boolean|integer|number|string|any|array|object)|((fn|(union|struct|_ext)(<([1-3])>)?)\\.([a-zA-Z_]\\w*))$'}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Fine': {'field': ['number']},},]}}],[{}, {'Ok_': {}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Fine': {'field': ['number']},},], 'extend!': 'wrong'}}],[{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [], 'reason': {'JsonInvalid': {}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Fine': {'field': ['number']},},], 'extend!': 'true'}}],[{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Broken': {}, 'unknown': False},]}}],[{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'unknown'], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct<1>.Broken': {'field': ['T.1']},}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'struct<1>.Broken', 'field', 0], 'reason': {'StringRegexMatchFailed': {'regex': '^(boolean|integer|number|string|any|array|object)|((fn|(union|struct|_ext)(<([1-3])>)?)\\.([a-zA-Z_]\\w*)|(T([0])))$'}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct<2>.Broken': {'field': ['T.2']},}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'struct<2>.Broken', 'field', 0], 'reason': {'StringRegexMatchFailed': {'regex': '^(boolean|integer|number|string|any|array|object)|((fn|(union|struct|_ext)(<([1-3])>)?)\\.([a-zA-Z_]\\w*)|(T([0-1])))$'}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Broken': {'field': ['struct.Unknown']},}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'struct.Broken', 'field', 0], 'reason': {'TypeUnknown': {'name': 'struct.Unknown'}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'_ext.Broken': {},}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0], 'reason': {'TypeExtensionImplementationMissing': {'name': '_ext.Broken'}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': None,'->': [{'Ok_': {}}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'fn.broken'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': False,'->': [{'Ok_': {}}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'fn.broken'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': 0,'->': [{'Ok_': {}}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'fn.broken'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': '','->': [{'Ok_': {}}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'fn.broken'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': [],'->': [{'Ok_': {}}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'fn.broken'], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {'field': None},'->': [{'Ok_': {}}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'fn.broken', 'field'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {'field': False},'->': [{'Ok_': {}}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'fn.broken', 'field'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {'field': 0},'->': [{'Ok_': {}}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'fn.broken', 'field'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {'field': ''},'->': [{'Ok_': {}}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'fn.broken', 'field'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {'field': {}},'->': [{'Ok_': {}}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'fn.broken', 'field'], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, '->'], 'reason': {'RequiredObjectKeyMissing': {}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {},'->': None}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, '->'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {},'->': False}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, '->'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {},'->': 0}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, '->'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {},'->': ''}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, '->'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {},'->': {}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, '->'], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {},'->': []}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, '->', 0, 'Ok_'], 'reason': {'RequiredObjectKeyMissing': {}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {},'->': [{'Ok_': {}},{'Wrong': None}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, '->', 1, 'Wrong'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {},'->': [{'Ok_': {}},{'Wrong': False}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, '->', 1, 'Wrong'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {},'->': [{'Ok_': {}},{'Wrong': 0}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, '->', 1, 'Wrong'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {},'->': [{'Ok_': {}},{'Wrong': ''}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, '->', 1, 'Wrong'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {},'->': [{'Ok_': {}},{'Wrong': []}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, '->', 1, 'Wrong'], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {},'->': [{'Ok_': {'field': None}}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, '->', 0, 'Ok_', 'field'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {},'->': [{'Ok_': {'field': False}}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, '->', 0, 'Ok_', 'field'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {},'->': [{'Ok_': {'field': 0}}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, '->', 0, 'Ok_', 'field'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {},'->': [{'Ok_': {'field': ''}}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, '->', 0, 'Ok_', 'field'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {},'->': [{'Ok_': {'field': {}}}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, '->', 0, 'Ok_', 'field'], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.fine': {},'->': [{'Ok_': {}}]}]}}], [{}, {'Ok_': {}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken_': {},'->': [{'Ok_': {}}], 'unknown': False}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'unknown'], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {},'->': [{'Ok_': {}}], '_errors': '^.*$'}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, '_errors'], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken_': {},'->': [{'Ok_': {}}], "_errors": None}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, '_errors'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken_': {},'->': [{'Ok_': {}}], "_errors": False}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, '_errors'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken_': {},'->': [{'Ok_': {}}], "_errors": 0}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, '_errors'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken_': {},'->': [{'Ok_': {}}], "_errors": []}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, '_errors'], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken_': {},'->': [{'Ok_': {}}], "_errors": {}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, '_errors'], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': None}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'union.Broken'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': False}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'union.Broken'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': 0}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'union.Broken'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': ''}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'union.Broken'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': {}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'union.Broken'], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': [None]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'union.Broken', 0], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': [False]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'union.Broken', 0], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': [0]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'union.Broken', 0], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': ['']}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'union.Broken', 0], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': [[]]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'union.Broken', 0], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': [{'Case': None}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'union.Broken', 0, 'Case'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': [{'Case': False}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'union.Broken', 0, 'Case'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': [{'Case': 0}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'union.Broken', 0, 'Case'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': [{'Case': ''}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'union.Broken', 0, 'Case'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': [{'Case': []}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'union.Broken', 0, 'Case'], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': [{'Case!': {}}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'union.Broken', 0], 'reason': {'ObjectKeyRegexMatchCountUnexpected': {'actual': 0, 'expected': 1, 'regex': '^([A-Z][a-zA-Z0-9_]*)$', 'keys': ['Case!']}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': [{'case': {}}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'union.Broken', 0], 'reason': {'ObjectKeyRegexMatchCountUnexpected': {'actual': 0, 'expected': 1, 'regex': '^([A-Z][a-zA-Z0-9_]*)$', 'keys': ['case']}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': [{'Case': {'field': None}}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'union.Broken', 0, 'Case', 'field'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': [{'Case': {'field': False}}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'union.Broken', 0, 'Case', 'field'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': [{'Case': {'field': 0}}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'union.Broken', 0, 'Case', 'field'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': [{'Case': {'field': ''}}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'union.Broken', 0, 'Case', 'field'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': [{'Case': {'field': {}}}]}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'union.Broken', 0, 'Case', 'field'], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': [{'Case': {'field': ['number']}}]}]}}], [{}, {'Ok_': {}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': []}]}}],[{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'union.Broken'], 'reason': {'EmptyArrayDisallowed': {}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': [{'Case': {}}], 'unknown': False},]}}],[{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'unknown'], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'requestHeader.field': None}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'requestHeader.field'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'requestHeader.field': False}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'requestHeader.field'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'requestHeader.field': 0}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'requestHeader.field'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'requestHeader.field': ''}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'requestHeader.field'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'requestHeader.field': {}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'requestHeader.field'], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'responseHeader.field': None}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'responseHeader.field'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'responseHeader.field': False}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'responseHeader.field'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'responseHeader.field': 0}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'responseHeader.field'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'responseHeader.field': ''}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'responseHeader.field'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'responseHeader.field': {}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0, 'responseHeader.field'], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'responseHeader.field': ['boolean']}, {'responseHeader.field': ['integer']}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [1, 'responseHeader.field'], 'reason': {'PathCollision': {'other': [0, 'responseHeader.field']}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'requestHeader.field': ['boolean']}, {'requestHeader.field': ['integer']}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [1, 'requestHeader.field'], 'reason': {'PathCollision': {'other': [0, 'requestHeader.field']}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'responseHeader.field': ['boolean']}, {'requestHeader.field': ['integer']}]}}], [{}, {'Ok_': {}}]],
        [[{}, {'fn.validateSchema': {'schema': [None]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [False]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [0]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': ['']}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [[]]}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [0], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'_serializeSchema': False}, {'fn.validateSchema': {'schema': 'badjson'}}], [{}, {'ErrorValidationFailure': {'cases': [{'document': 'auto_', 'path': [], 'reason': {'JsonInvalid': {}}}]}}]]
    ]
}