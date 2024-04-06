cases = {
    'schema': [
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Example': {}}, {'struct.Example': {}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'path': [1, 'struct.Example'], 'reason': {'PathCollision': {'other': [0, 'struct.Example']}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Example': {}}, {'union.Example': {"Case": {}}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'path': [1, 'union.Example'], 'reason': {'PathCollision': {'other': [0, 'struct.Example']}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Example': {}}, {'fn.Example': {}, "->": {"Ok": {}}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'path': [1, 'fn.Example'], 'reason': {'PathCollision': {'other': [0, 'struct.Example']}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Example': {"Case": {}}}, {'struct.Example': {}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'path': [1, 'struct.Example'], 'reason': {'PathCollision': {'other': [0, 'union.Example']}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Example': {"Case": {}}}, {'fn.Example': {}, "->": {"Ok": {}}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'path': [1, 'fn.Example'], 'reason': {'PathCollision': {'other': [0, 'union.Example']}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.Example': {}, "->": {"Ok": {}}}, {'struct.Example': {}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'path': [1, 'struct.Example'], 'reason': {'PathCollision': {'other': [0, 'fn.Example']}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.Example': {}, "->": {"Ok": {}}}, {'union.Example': {"Case": {}}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'path': [1, 'union.Example'], 'reason': {'PathCollision': {'other': [0, 'fn.Example']}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Example': {'field': ['boolean'], 'field!': ['integer']}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'struct.Example', 'path': [0, 'struct.Example', 'field!'], 'reason': {'PathCollision': {'other': [0, 'struct.Example', 'field']}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Example': {'field!': ['boolean'], 'field': ['integer']}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'struct.Example', 'path': [0, 'struct.Example', 'field'], 'reason': {'PathCollision': {'other': [0, 'struct.Example', 'field!']}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'invalid.Example': {}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'path': [0], 'reason': {'ObjectKeyRegexMatchCountUnexpected': {'regex': '^((fn|errors|info|headers)|((struct|union|_ext)(<[0-2]>)?))\\..*', 'actual': 0, 'expected': 1}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': None}}], [{}, {'ErrorValidationFailure': {'cases': [{'path': [], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': False}}], [{}, {'ErrorValidationFailure': {'cases': [{'path': [], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': 0}}], [{}, {'ErrorValidationFailure': {'cases': [{'path': [], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': ''}}], [{}, {'ErrorValidationFailure': {'cases': [{'path': [], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': {}}}], [{}, {'ErrorValidationFailure': {'cases': [{'path': [], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.example': {},'->': {'Ok': {},"Err": {}}},{'errors.Collide': {'Err': {}}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'errors.Collide', 'path': [1, 'errors.Collide', 'Err'], 'reason': {'PathCollision': {'other': [0, '->', 'Err']}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'errors.Broken': {}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'errors.Broken', 'path': [0, 'errors.Broken'], 'reason': {'EmptyObjectDisallowed': {}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'errors.Broken': {'Err': {}}, 'unknown': False}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'errors.Broken', 'path': [0, 'unknown'], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'errors.Broken': {'Err': {}, 'unknown': False}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'errors.Broken', 'path': [0, 'errors.Broken', 'unknown'], 'reason': {'KeyRegexMatchFailed': {'regex': '^(_?[A-Z][a-zA-Z0-9_]*)$'}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'errors.Broken': {'wrong': {}}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'errors.Broken', 'path': [0, 'errors.Broken', 'wrong'], 'reason': {'KeyRegexMatchFailed': {'regex': '^(_?[A-Z][a-zA-Z0-9_]*)$'}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'errors.Example': ['wrong']}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'errors.Example', 'path': [0, 'errors.Example'], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Example': {'@invalid': []}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'struct.Example', 'path': [0, 'struct.Example', '@invalid'], 'reason': {'KeyRegexMatchFailed': {'regex': '^(_?[a-z][a-zA-Z0-9_]*)(!)?$'}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Example': {'field': []}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'struct.Example', 'path': [0, 'struct.Example', 'field'], 'reason': {'EmptyArrayDisallowed': {}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Example': {'field': [None]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'struct.Example', 'path': [0, 'struct.Example', 'field', 0], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Example': {'field': [False]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'struct.Example', 'path': [0, 'struct.Example', 'field', 0], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Example': {'field': [0]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'struct.Example', 'path': [0, 'struct.Example', 'field', 0], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Example': {'field': [[]]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'struct.Example', 'path': [0, 'struct.Example', 'field', 0], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Example': {'field': [{}]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'struct.Example', 'path': [0, 'struct.Example', 'field', 0], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Example': {'field': ['']}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'struct.Example', 'path': [0, 'struct.Example', 'field', 0], 'reason': {'StringRegexMatchFailed': {'regex': '^(.+?)(\\?)?$'}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct<1>.Example': {'field': ['T.0?']}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'struct<1>.Example', 'path': [0, 'struct<1>.Example', 'field', 0], 'reason': {'StringRegexMatchFailed': {'regex': '^(.+?)[^\\?]$'}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct<1>.Param': {'field': ['T.0']},'struct.Example': {'field': ['struct<1>.Param']}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'path': [0], 'reason': {'ObjectKeyRegexMatchCountUnexpected': {'regex': '^((fn|errors|info|headers)|((struct|union|_ext)(<[0-2]>)?))\\..*', 'actual': 2, 'expected': 1}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct<1>.Param': {'field': ['T.0']},},{'struct.Example': {'field': ['struct<1>.Param']}}]}}],[{}, {'ErrorValidationFailure': {'cases': [{'key!': 'struct.Example', 'path': [1, 'struct.Example', 'field'], 'reason': {'ArrayLengthUnexpected': {'actual': 1, 'expected': 2}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct<1>.Param': {'field': ['T.0']},},{'struct.Example': {'field': ['struct<1>.Param', None]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'struct.Example', 'path': [1, 'struct.Example', 'field', 1], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct<1>.Param': {'field': ['T.0']},},{'struct.Example': {'field': ['struct<1>.Param', False]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'struct.Example', 'path': [1, 'struct.Example', 'field', 1], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct<1>.Param': {'field': ['T.0']},},{'struct.Example': {'field': ['struct<1>.Param', 0]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'struct.Example', 'path': [1, 'struct.Example', 'field', 1], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct<1>.Param': {'field': ['T.0']},},{'struct.Example': {'field': ['struct<1>.Param', '']}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'struct.Example', 'path': [1, 'struct.Example', 'field', 1], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct<1>.Param': {'field': ['T.0']},},{'struct.Example': {'field': ['struct<1>.Param', {}]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'struct.Example', 'path': [1, 'struct.Example', 'field', 1], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct<1>.Param': {'field': ['T.0']},},{'struct.Example': {'field': ['struct<1>.Param', [None]]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'struct.Example', 'path': [1, 'struct.Example', 'field', 1, 0], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct<1>.Param': {'field': ['T.0']},},{'struct.Example': {'field': ['struct<1>.Param', [False]]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'struct.Example', 'path': [1, 'struct.Example', 'field', 1, 0], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct<1>.Param': {'field': ['T.0']},},{'struct.Example': {'field': ['struct<1>.Param', [0]]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'struct.Example', 'path': [1, 'struct.Example', 'field', 1, 0], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct<1>.Param': {'field': ['T.0']},},{'struct.Example': {'field': ['struct<1>.Param', [[]]]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'struct.Example', 'path': [1, 'struct.Example', 'field', 1, 0], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct<1>.Param': {'field': ['T.0']},},{'struct.Example': {'field': ['struct<1>.Param', [{}]]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'struct.Example', 'path': [1, 'struct.Example', 'field', 1, 0], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Example': {'field': ['struct.Broken']},},{'struct.Example2': {'field': ['struct.Broken']},},{'struct.Broken': {'field': [None]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'struct.Broken', 'path': [2, 'struct.Broken', 'field', 0], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Example': {'field': ['struct.Broken']},},{'struct.Example2': {'field': ['struct.Broken']},},{'struct.Broken': {'field': [False]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'struct.Broken', 'path': [2, 'struct.Broken', 'field', 0], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Example': {'field': ['struct.Broken']},},{'struct.Example2': {'field': ['struct.Broken']},},{'struct.Broken': {'field': [0]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'struct.Broken', 'path': [2, 'struct.Broken', 'field', 0], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Example': {'field': ['struct.Broken']},},{'struct.Example2': {'field': ['struct.Broken']},},{'struct.Broken': {'field': [[]]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'struct.Broken', 'path': [2, 'struct.Broken', 'field', 0], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Example': {'field': ['struct.Broken']},},{'struct.Example2': {'field': ['struct.Broken']},},{'struct.Broken': {'field': [{}]}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'struct.Broken', 'path': [2, 'struct.Broken', 'field', 0], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Broken': {'field': ['wrong']},},]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'struct.Broken', 'path': [0, 'struct.Broken', 'field', 0], 'reason': {'StringRegexMatchFailed': {'regex': '^(boolean|integer|number|string|any|array|object)|((fn|(union|struct|_ext)(<([1-3])>)?)\\.([a-zA-Z_]\\w*))$'}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Fine': {'field': ['number']},},]}}],[{}, {'Ok': {}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Fine': {'field': ['number']},},], 'extend!': 'wrong'}}],[{}, {'ErrorValidationFailure': {'cases': [{'path': [], 'reason': {'JsonInvalid': {}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Fine': {'field': ['number']},},], 'extend!': 'true'}}],[{}, {'ErrorValidationFailure': {'cases': [{'path': [], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Broken': {}, 'unknown': False},]}}],[{}, {'ErrorValidationFailure': {'cases': [{'key!': 'struct.Broken', 'path': [0, 'unknown'], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct<1>.Broken': {'field': ['T.1']},}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'struct<1>.Broken', 'path': [0, 'struct<1>.Broken', 'field', 0], 'reason': {'StringRegexMatchFailed': {'regex': '^(boolean|integer|number|string|any|array|object)|((fn|(union|struct|_ext)(<([1-3])>)?)\\.([a-zA-Z_]\\w*)|(T.([0])))$'}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct<2>.Broken': {'field': ['T.2']},}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'struct<2>.Broken', 'path': [0, 'struct<2>.Broken', 'field', 0], 'reason': {'StringRegexMatchFailed': {'regex': '^(boolean|integer|number|string|any|array|object)|((fn|(union|struct|_ext)(<([1-3])>)?)\\.([a-zA-Z_]\\w*)|(T.([0-1])))$'}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'struct.Broken': {'field': ['struct.Unknown']},}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'struct.Broken', 'path': [0, 'struct.Broken', 'field', 0], 'reason': {'TypeUnknown': {'name': 'struct.Unknown'}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'_ext.Broken': {},}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': '_ext.Broken', 'path': [0], 'reason': {'TypeExtensionImplementationMissing': {'name': '_ext.Broken'}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': None,'->': {'Ok': {}}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'fn.broken', 'path': [0, 'fn.broken'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': False,'->': {'Ok': {}}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'fn.broken', 'path': [0, 'fn.broken'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': 0,'->': {'Ok': {}}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'fn.broken', 'path': [0, 'fn.broken'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': '','->': {'Ok': {}}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'fn.broken', 'path': [0, 'fn.broken'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': [],'->': {'Ok': {}}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'fn.broken', 'path': [0, 'fn.broken'], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {'field': None},'->': {'Ok': {}}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'fn.broken', 'path': [0, 'fn.broken', 'field'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {'field': False},'->': {'Ok': {}}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'fn.broken', 'path': [0, 'fn.broken', 'field'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {'field': 0},'->': {'Ok': {}}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'fn.broken', 'path': [0, 'fn.broken', 'field'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {'field': ''},'->': {'Ok': {}}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'fn.broken', 'path': [0, 'fn.broken', 'field'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {'field': {}},'->': {'Ok': {}}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'fn.broken', 'path': [0, 'fn.broken', 'field'], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'fn.broken', 'path': [0, '->'], 'reason': {'RequiredObjectKeyMissing': {}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {},'->': None}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'fn.broken', 'path': [0, '->'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {},'->': False}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'fn.broken', 'path': [0, '->'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {},'->': 0}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'fn.broken', 'path': [0, '->'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {},'->': ''}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'fn.broken', 'path': [0, '->'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {},'->': []}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'fn.broken', 'path': [0, '->'], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {},'->': {}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'fn.broken', 'path': [0, '->', 'Ok'], 'reason': {'RequiredObjectKeyMissing': {}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {},'->': {'Ok': {},'Wrong': None}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'fn.broken', 'path': [0, '->', 'Wrong'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {},'->': {'Ok': {},'Wrong': False}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'fn.broken', 'path': [0, '->', 'Wrong'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {},'->': {'Ok': {},'Wrong': 0}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'fn.broken', 'path': [0, '->', 'Wrong'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {},'->': {'Ok': {},'Wrong': ''}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'fn.broken', 'path': [0, '->', 'Wrong'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {},'->': {'Ok': {},'Wrong': []}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'fn.broken', 'path': [0, '->', 'Wrong'], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {},'->': {'Ok': {'field': None},}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'fn.broken', 'path': [0, '->', 'Ok', 'field'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {},'->': {'Ok': {'field': False},}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'fn.broken', 'path': [0, '->', 'Ok', 'field'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {},'->': {'Ok': {'field': 0},}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'fn.broken', 'path': [0, '->', 'Ok', 'field'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {},'->': {'Ok': {'field': ''},}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'fn.broken', 'path': [0, '->', 'Ok', 'field'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {},'->': {'Ok': {'field': {}},}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'fn.broken', 'path': [0, '->', 'Ok', 'field'], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.fine': {},'->': {'Ok': {}}}]}}], [{}, {'Ok': {}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken_': {},'->': {'Ok': {}}, 'unknown': False}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'fn.broken_', 'path': [0, 'unknown'], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken': {},'->': {'Ok': {}}, '_errors': '^.*$'}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'fn.broken', 'path': [0, '_errors'], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken_': {},'->': {'Ok': {}}, "_errors": None}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'fn.broken_', 'path': [0, '_errors'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken_': {},'->': {'Ok': {}}, "_errors": False}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'fn.broken_', 'path': [0, '_errors'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken_': {},'->': {'Ok': {}}, "_errors": 0}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'fn.broken_', 'path': [0, '_errors'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken_': {},'->': {'Ok': {}}, "_errors": []}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'fn.broken_', 'path': [0, '_errors'], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'fn.broken_': {},'->': {'Ok': {}}, "_errors": {}}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'fn.broken_', 'path': [0, '_errors'], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'String': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': {'Case': None},}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'union.Broken', 'path': [0, 'union.Broken', 'Case'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': {'Case': False},}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'union.Broken', 'path': [0, 'union.Broken', 'Case'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': {'Case': 0},}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'union.Broken', 'path': [0, 'union.Broken', 'Case'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': {'Case': ''},}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'union.Broken', 'path': [0, 'union.Broken', 'Case'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': {'Case': []},}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'union.Broken', 'path': [0, 'union.Broken', 'Case'], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': {'Case!': {}},}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'union.Broken', 'path': [0, 'union.Broken', 'Case!'], 'reason': {'KeyRegexMatchFailed': {'regex': '^(_?[A-Z][a-zA-Z0-9_]*)$'}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': {'case': {}},}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'union.Broken', 'path': [0, 'union.Broken', 'case'], 'reason': {'KeyRegexMatchFailed': {'regex': '^(_?[A-Z][a-zA-Z0-9_]*)$'}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': {'Case': {'field': None}},}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'union.Broken', 'path': [0, 'union.Broken', 'Case', 'field'], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': {'Case': {'field': False}},}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'union.Broken', 'path': [0, 'union.Broken', 'Case', 'field'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': {'Case': {'field': 0}},}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'union.Broken', 'path': [0, 'union.Broken', 'Case', 'field'], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': {'Case': {'field': ''}},}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'union.Broken', 'path': [0, 'union.Broken', 'Case', 'field'], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': {'Case': {'field': {}}},}]}}], [{}, {'ErrorValidationFailure': {'cases': [{'key!': 'union.Broken', 'path': [0, 'union.Broken', 'Case', 'field'], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Array': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': {'Case': {'field': ['number']}},}]}}], [{}, {'Ok': {}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': {}}]}}],[{}, {'ErrorValidationFailure': {'cases': [{'key!': 'union.Broken', 'path': [0, 'union.Broken'], 'reason': {'EmptyObjectDisallowed': {}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [{'union.Broken': {'Case': {}}, 'unknown': False},]}}],[{}, {'ErrorValidationFailure': {'cases': [{'key!': 'union.Broken', 'path': [0, 'unknown'], 'reason': {'ObjectKeyDisallowed': {}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [None]}}], [{}, {'ErrorValidationFailure': {'cases': [{'path': [0], 'reason': {'TypeUnexpected': {'actual': {'Null': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [False]}}], [{}, {'ErrorValidationFailure': {'cases': [{'path': [0], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [0]}}], [{}, {'ErrorValidationFailure': {'cases': [{'path': [0], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': ['']}}], [{}, {'ErrorValidationFailure': {'cases': [{'path': [0], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{}, {'fn.validateSchema': {'schema': [[]]}}], [{}, {'ErrorValidationFailure': {'cases': [{'path': [0], 'reason': {'TypeUnexpected': {'actual': {'Array': {}}, 'expected': {'Object': {}}}}}]}}]],
        [[{'_serializeSchema': False}, {'fn.validateSchema': {'schema': 'badjson'}}], [{}, {'ErrorValidationFailure': {'cases': [{'path': [], 'reason': {'JsonInvalid': {}}}]}}]]
    ]
}