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
                                    'field': []
                                }
                            }
                        ]
                    }
                }
            ],
            [{}, {'errorValidationFailure': {
                'cases': [{'path': [0, 'struct.Example', 'field'], 'reason': {'ArrayMustNotBeEmpty': {}}}]}}]
        ],
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': [
                            {
                                'struct.Example': {
                                    'field': [False]
                                }
                            }
                        ]
                    }
                }
            ],
            [{}, {'errorValidationFailure': {
                'cases': [{'path': [0, 'struct.Example', 'field', 0], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'String': {}}}}}]}}]
        ],
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': [
                            {
                                'struct.Example': {
                                    'field': ['']
                                }
                            }
                        ]
                    }
                }
            ],
            [{}, {'errorValidationFailure': {
                'cases': [{'path': [0, 'struct.Example', 'field', 0], 'reason': {'StringRegexMatchFailed': {'regex': '^(.+?)(\\?)?$'}}}]}}]
        ],
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': [
                            {
                                'struct<1>.Example': {
                                    'field': ['T.0?']
                                }
                            }
                        ]
                    }
                }
            ],
            [{}, {'errorValidationFailure': {
                'cases': [{'path': [0, 'struct<1>.Example', 'field', 0], 'reason': {'NullableGenericDisallowed': {}}}]}}]
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
                                    'field': ['struct<1>.Param']
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
                                    'field': ['struct<1>.Param']
                                }
                            }
                        ]
                    }
                }
            ],
            [{}, {'errorValidationFailure': {
                'cases': [{'path': [1, 'struct.Example', 'field'], 'reason': {'ArrayLengthUnexpected': {'actual': 1, 'expected': 2}}}]}}]
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
                                    'field': ['struct<1>.Param', False]
                                }
                            }
                        ]
                    }
                }
            ],
            [{}, {'errorValidationFailure': {
                'cases': [{'path': [1, 'struct.Example', 'field', 1], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Array': {}}}}}]}}]
        ],
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': [
                            {
                                'struct.Example': {
                                    'field': ['struct.Broken']
                                },
                            },
                            {
                                'struct.Example2': {
                                    'field': ['struct.Broken']
                                },
                            },
                            {
                                'struct.Broken': {
                                    'field': [False]
                                }
                            }
                        ]
                    }
                }
            ],
            [{}, {'errorValidationFailure': {
                'cases': [{'path': [2, 'struct.Broken', 'field', 0], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'String': {}}}}}]}}]
        ],
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': [
                            {
                                'struct.Broken': {
                                    'field': ['wrong']
                                },
                            },
                        ]
                    }
                }
            ],
            [{}, {'errorValidationFailure': {
                'cases': [{'path': [0, 'struct.Broken', 'field', 0], 'reason': {'StringRegexMatchFailed': {'regex': '^(boolean|integer|number|string|any|array|object|T.([0-2]))|((trait|info|fn|(union|struct|ext)(<([1-3])>)?)\\.([a-zA-Z_]\\w*))$'}}}]}}]
        ],        
    ]
}
