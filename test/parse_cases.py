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
                'cases': [{'path': [1], 'reason': {'DuplicateSchemaKey': {'schemaKey': 'struct.Example'}}}]}}]
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
                'cases': [{'path': [0], 'reason': {'DefinitionMustHaveOneKeyMatchingRegex': {'regex': '^((fn|trait|info)|((struct|union|ext)(<[0-2]>)?))\\..*'}}}]}}]
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
                'cases': [{'path': [], 'reason': {'ArrayTypeRequired': {}}}]}}]
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
                'cases': [{'path': [], 'reason': {'ArrayTypeRequired': {}}}]}}]
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
                'cases': [{'path': [], 'reason': {'ArrayTypeRequired': {}}}]}}]
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
                'cases': [{'path': [], 'reason': {'ArrayTypeRequired': {}}}]}}]
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
                'cases': [{'path': [1, 'trait.Collide', 'fn.*', 'arg1'], 'reason': {'TraitArgumentFieldAlreadyInUseByFunction': {"fn": "fn.example"}}}]}}]
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
                'cases': [{'path': [1, 'trait.Collide', '->', 'err'], 'reason': {'TraitResultValueAlreadyInUseByFunction': {"fn": "fn.example"}}}]}}]
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
                'cases': [{'path': [0, 'trait.Example'], 'reason': {'ObjectTypeRequired': {}}}]}}]
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
                'cases': [{'path': [0, 'trait.Example'], 'reason': {'InvalidTrait': {}}}]}}]
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
                'cases': [{'path': [0, 'trait.Example', 'fn._?*'], 'reason': {'TraitDefinitionCannotTargetInternalFunctions': {}}}]}}]
        ],
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': [
                            {
                                'struct.Example': {
                                    'wrong': []
                                }
                            }
                        ]
                    }
                }
            ],
            [{}, {'errorValidationFailure': {
                'cases': [{'path': [0, 'struct.Example', 'wrong'], 'reason': {'ArrayMustNotBeEmpty': {}}}]}}]
        ],
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': [
                            {
                                'struct.Example': {
                                    'wrong': [False]
                                }
                            }
                        ]
                    }
                }
            ],
            [{}, {'errorValidationFailure': {
                'cases': [{'path': [0, 'struct.Example', 'wrong', 0], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'String': {}}}}}]}}]
        ],
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': [
                            {
                                'struct.Example': {
                                    'wrong': ['']
                                }
                            }
                        ]
                    }
                }
            ],
            [{}, {'errorValidationFailure': {
                'cases': [{'path': [0, 'struct.Example', 'wrong', 0], 'reason': {'StringRegexMatchFailed': {'regex': '^(.+?)(\\?)?$'}}}]}}]
        ],
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': [
                            {
                                'struct<1>.Example': {
                                    'wrong': ['T.0?']
                                }
                            }
                        ]
                    }
                }
            ],
            [{}, {'errorValidationFailure': {
                'cases': [{'path': [0, 'struct<1>.Example', 'wrong', 0], 'reason': {'NullableGenericDisallowed': {}}}]}}]
        ],
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': [
                            {
                                'struct<1>.Param': {
                                    'field': ['T.0']
                                },
                                'struct.Example': {
                                    'wrong': ['struct<1>.Param']
                                }
                            }
                        ]
                    }
                }
            ],
            [{}, {'errorValidationFailure': {
                'cases': [{'path': [0], 'reason': {'DefinitionMustHaveOneKeyMatchingRegex': {'regex': '^((fn|trait|info)|((struct|union|ext)(<[0-2]>)?))\\..*'}}}]}}]
        ],        
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': [
                            {
                                'struct<1>.Param': {
                                    'field': ['T.0']
                                },
                            },
                            {
                                'struct.Example': {
                                    'wrong': ['struct<1>.Param']
                                }
                            }
                        ]
                    }
                }
            ],
            [{}, {'errorValidationFailure': {
                'cases': [{'path': [1, 'struct.Example', 'wrong'], 'reason': {'ArrayLengthUnexpected': {'actual': 1, 'expected': 2}}}]}}]
        ],        
    ]
}
