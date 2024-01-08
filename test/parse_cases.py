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
            [{}, {'ErrorValidationFailure': {
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
            [{}, {'ErrorValidationFailure': {
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
            [{}, {'ErrorValidationFailure': {
                'cases': [{'path': [], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Array': {}}}}}]}}]
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
            [{}, {'ErrorValidationFailure': {
                'cases': [{'path': [], 'reason': {'TypeUnexpected': {'actual': {'Number': {}}, 'expected': {'Array': {}}}}}]}}]
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
            [{}, {'ErrorValidationFailure': {
                'cases': [{'path': [], 'reason': {'TypeUnexpected': {'actual': {'String': {}}, 'expected': {'Array': {}}}}}]}}]
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
            [{}, {'ErrorValidationFailure': {
                'cases': [{'path': [], 'reason': {'TypeUnexpected': {'actual': {'Object': {}}, 'expected': {'Array': {}}}}}]}}]
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
            [{}, {'ErrorValidationFailure': {
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
                                    "Err": {}
                                }
                            },
                            {
                                'trait.Collide': {
                                    'fn.*': {},
                                    '->': {
                                        'Err': {}
                                    }
                                }
                            }
                        ]

                    }
                }
            ],
            [{}, {'ErrorValidationFailure': {
                'cases': [{'path': [1, 'trait.Collide', '->', 'Err'], 'reason': {'TraitResultValueAlreadyInUseByFunction': {"fn": "fn.example"}}}]}}]
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
            [{}, {'ErrorValidationFailure': {
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
            [{}, {'ErrorValidationFailure': {
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
            [{}, {'ErrorValidationFailure': {
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
            [{}, {'ErrorValidationFailure': {
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
            [{}, {'ErrorValidationFailure': {
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
            [{}, {'ErrorValidationFailure': {
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
            [{}, {'ErrorValidationFailure': {
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
            [{}, {'ErrorValidationFailure': {
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
            [{}, {'ErrorValidationFailure': {
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
            [{}, {'ErrorValidationFailure': {
                'cases': [{'path': [1, 'struct.Example', 'field', 1], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Array': {}}}}}]}}]
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
                                    'field': ['struct<1>.Param', [False]]
                                }
                            }
                        ]
                    }
                }
            ],
            [{}, {'ErrorValidationFailure': {
                'cases': [{'path': [1, 'struct.Example', 'field', 1, 0], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'String': {}}}}}]}}]
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
            [{}, {'ErrorValidationFailure': {
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
            [{}, {'ErrorValidationFailure': {
                'cases': [{'path': [0, 'struct.Broken', 'field', 0], 'reason': {'StringRegexMatchFailed': {'regex': '^(boolean|integer|number|string|any|array|object)|((fn|(union|struct|ext)(<([1-3])>)?)\\.([a-zA-Z_]\\w*))$'}}}]}}]
        ],
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': [
                            {
                                'struct.Fine': {
                                    'field': ['number']
                                },
                            },
                        ]
                    }
                }
            ],
            [{}, {'Ok': {}}]
        ],
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': [
                            {
                                'struct<1>.Broken': {
                                    'field': ['T.1']
                                },
                            }
                        ]
                    }
                }
            ],
            [{}, {'ErrorValidationFailure': {
                'cases': [{'path': [0, 'struct<1>.Broken', 'field', 0], 'reason': {'StringRegexMatchFailed': {'regex': '^(boolean|integer|number|string|any|array|object)|((fn|(union|struct|ext)(<([1-3])>)?)\\.([a-zA-Z_]\\w*)|(T.([0])))$'}}}]}}]
        ],
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': [
                            {
                                'struct<2>.Broken': {
                                    'field': ['T.2']
                                },
                            }
                        ]
                    }
                }
            ],
            [{}, {'ErrorValidationFailure': {
                'cases': [{'path': [0, 'struct<2>.Broken', 'field', 0], 'reason': {'StringRegexMatchFailed': {'regex': '^(boolean|integer|number|string|any|array|object)|((fn|(union|struct|ext)(<([1-3])>)?)\\.([a-zA-Z_]\\w*)|(T.([0-1])))$'}}}]}}]
        ],
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': [
                            {
                                'struct.Broken': {
                                    'field': ['struct.Unknown']
                                },
                            }
                        ]
                    }
                }
            ],
            [{}, {'ErrorValidationFailure': {
                'cases': [{'path': [0, 'struct.Broken', 'field', 0], 'reason': {'TypeUnknown': {'name': 'struct.Unknown'}}}]}}]
        ],
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': [
                            {
                                'ext.Broken': {
                                },
                            }
                        ]
                    }
                }
            ],
            [{}, {'ErrorValidationFailure': {
                'cases': [{'path': [0], 'reason': {'TypeExtensionImplementationMissing': {'name': 'ext.Broken'}}}]}}]
        ],
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': [
                            {
                                'fn.broken': False,
                                '->': {
                                    "Ok": {}
                                }
                            }
                        ]
                    }
                }
            ],
            [{}, {'ErrorValidationFailure': {
                'cases': [{'path': [0, 'fn.broken'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Object': {}}}}}]}}]
        ],        
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': [
                            {
                                'fn.broken': {
                                    "field": False
                                },
                                '->': {
                                    "Ok": {}
                                }
                            }
                        ]
                    }
                }
            ],
            [{}, {'ErrorValidationFailure': {
                'cases': [{'path': [0, 'fn.broken', 'field'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Array': {}}}}}]}}]
        ],
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': [
                            {
                                'fn.broken': {
                                },
                                '->': False
                            }
                        ]
                    }
                }
            ],
            [{}, {'ErrorValidationFailure': {
                'cases': [{'path': [0, '->'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Object': {}}}}}]}}]
        ],
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': [
                            {
                                'fn.broken': {
                                },
                                '->': {
                                }
                            }
                        ]
                    }
                }
            ],
            [{}, {'ErrorValidationFailure': {
                'cases': [{'path': [0, '->', 'Ok'], 'reason': {'RequiredObjectKeyMissing': {}}}]}}]
        ],
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': [
                            {
                                'fn.broken': {
                                },
                                '->': {
                                    'Ok': {},
                                    'Wrong': False
                                }
                            }
                        ]
                    }
                }
            ],
            [{}, {'ErrorValidationFailure': {
                'cases': [{'path': [0, '->', 'Wrong'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Object': {}}}}}]}}]
        ],
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': [
                            {
                                'fn.broken': {
                                },
                                '->': {
                                    'Ok': {
                                        'field': False
                                    },
                                }
                            }
                        ]
                    }
                }
            ],
            [{}, {'ErrorValidationFailure': {
                'cases': [{'path': [0, '->', 'Ok', 'field'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Array': {}}}}}]}}]
        ],
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': [
                            {
                                'union.Broken': {
                                    'Case': False
                                },
                            }
                        ]
                    }
                }
            ],
            [{}, {'ErrorValidationFailure': {
                'cases': [{'path': [0, 'union.Broken', 'Case'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Object': {}}}}}]}}]
        ],
        [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': [
                            {
                                'union.Broken': {
                                    'Case!': {}
                                },
                            }
                        ]
                    }
                }
            ],
            [{}, {'ErrorValidationFailure': {
                'cases': [{'path': [0, 'union.Broken', 'Case!'], 'reason': {'StringRegexMatchFailed': {'regex': '^(_?[A-Z][a-zA-Z0-9_]*)$'}}}]}}]
        ],
       [
            [
                {},
                {
                    'fn.validateSchema': {
                        'schema': [
                            {
                                'union.Broken': {
                                    'Case': {
                                        'field': False
                                    }
                                },
                            }
                        ]
                    }
                }
            ],
            [{}, {'ErrorValidationFailure': {
                'cases': [{'path': [0, 'union.Broken', 'Case', 'field'], 'reason': {'TypeUnexpected': {'actual': {'Boolean': {}}, 'expected': {'Array': {}}}}}]}}]
        ],
    ]
}
