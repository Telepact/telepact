cases = {
    'schema': [
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': [
                            {
                                'struct.Example': {}
                            },
                            {
                                'struct.Example': {}
                            }
                        ]
                    }
                }
            ],
            [{}, {'errorValidationFailure': {
                'cases': [{'path': '[1]', 'reason': {'DuplicateSchemaKey': {'schemaKey': 'struct.Example'}}}]}}]
        ],
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': [
                            {
                                'invalid.Example': {}
                            }
                        ]

                    }
                }
            ],
            [{}, {'errorValidationFailure': {
                'cases': [{'path': '[0]', 'reason': {'DefinitionMustHaveOneKeyMatchingRegex': {'regex': '^((fn|trait|info)|((struct|enum|ext)(<[0-2]>)?))\\..*'}}}]}}]
        ],
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': False
                    }
                }
            ],
            [{}, {'errorValidationFailure': {
                'cases': [{'path': '(document-root)', 'reason': {'ArrayTypeRequired': {}}}]}}]
        ],
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': 0
                    }
                }
            ],
            [{}, {'errorValidationFailure': {
                'cases': [{'path': '(document-root)', 'reason': {'ArrayTypeRequired': {}}}]}}]
        ],
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': ''
                    }
                }
            ],
            [{}, {'errorValidationFailure': {
                'cases': [{'path': '(document-root)', 'reason': {'ArrayTypeRequired': {}}}]}}]
        ],
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': {}
                    }
                }
            ],
            [{}, {'errorValidationFailure': {
                'cases': [{'path': '(document-root)', 'reason': {'ArrayTypeRequired': {}}}]}}]
        ],
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': [
                            {
                                'fn.example': {
                                    'arg1': ['boolean']
                                },
                                '->': {
                                    'Ok': {}
                                }
                            },
                            {
                                'trait.Collide': {
                                    'fn.*': {
                                        'arg1': ['boolean']
                                    },
                                    '->': {}
                                }
                            }
                        ]

                    }
                }
            ],
            [{}, {'errorValidationFailure': {
                'cases': [{'path': '[1].trait.Collide.fn.*.arg1', 'reason': {'TraitArgumentFieldAlreadyInUseByFunction': {"fn": "fn.example"}}}]}}]
        ],
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': [
                            {
                                'fn.example': {},
                                '->': {
                                    'Ok': {},
                                    "err": {}
                                }
                            },
                            {
                                'trait.Collide': {
                                    'fn.*': {},
                                    '->': {
                                        'err': {}
                                    }
                                }
                            }
                        ]

                    }
                }
            ],
            [{}, {'errorValidationFailure': {
                'cases': [{'path': '[1].trait.Collide.->.err', 'reason': {'TraitResultValueAlreadyInUseByFunction': {"fn": "fn.example"}}}]}}]
        ],
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': [
                            {
                                'trait.Example': ['wrong']
                            }
                        ]
                    }
                }
            ],
            [{}, {'errorValidationFailure': {
                'cases': [{'path': '[0].trait.Example', 'reason': {'ObjectTypeRequired': {}}}]}}]
        ],
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': [
                            {
                                'trait.Example': {
                                    'fn._*': {},
                                    '->': {}
                                }
                            }
                        ]
                    }
                }
            ],
            [{}, {'errorValidationFailure': {
                'cases': [{'path': '[0].trait.Example', 'reason': {'InvalidTrait': {}}}]}}]
        ],
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': [
                            {
                                'trait.Example': {
                                    'fn._?*': {},
                                    '->': {}
                                }
                            }
                        ]

                    }
                }
            ],
            [{}, {'errorValidationFailure': {
                'cases': [{'path': '[0].trait.Example', 'reason': {'TraitDefinitionCannotTargetInternalFunctions': {}}}]}}]
        ],
    ]
}
