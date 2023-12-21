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
                'cases': [{'path': '(root)', 'reason': {'InvalidRoot': {}}}]}}]
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
                'cases': [{'path': '(root)', 'reason': {'InvalidRoot': {}}}]}}]
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
                'cases': [{'path': '(root)', 'reason': {'InvalidRoot': {}}}]}}]
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
                'cases': [{'path': '(root)', 'reason': {'InvalidRoot': {}}}]}}]
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
                                    'ok': {}
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
                'cases': [{'path': '(root)', 'reason': {'InvalidTrait': {}}}]}}]
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
                                    'ok': {
                                        'result1': ['boolean']
                                    }
                                }
                            },
                            {
                                'trait.Collide': {
                                    'fn.*': {},
                                    '->': {
                                        'ok': {
                                            'result1': ['boolean']
                                        }
                                    }
                                }
                            }
                        ]

                    }
                }
            ],
            [{}, {'errorValidationFailure': {
                'cases': [{'path': '(root)', 'reason': {'InvalidTrait': {}}}]}}]
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
                'cases': [{'path': '(root)', 'reason': {'InvalidTrait': {}}}]}}]
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
                'cases': [{'path': '(root)', 'reason': {'InvalidTrait': {}}}]}}]
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
                'cases': [{'path': '(root)', 'reason': {'InvalidTrait': {}}}]}}]
        ],
    ]
}
