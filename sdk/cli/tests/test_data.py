compare_cases: list = [
    (
        [
            {
                "fn.test": {
                    "arg1": "boolean"
                },
                "->": [
                    {
                        "Ok_": {
                            "res1": "boolean"
                        }
                    }
                ]
            }
        ],
        [
            {
                "fn.test": {
                    "arg1": "boolean"
                },
                "->": [
                    {
                        "Ok_": {
                            "res1": "boolean"
                        }
                    }
                ]
            }
        ],
        [],
        0
    ),
    (
        [
            {
                "fn.test": {
                    "arg1": "boolean"
                },
                "->": [
                    {
                        "Ok_": {
                            "res1": "boolean"
                        }
                    }
                ]
            }
        ],
        [
            {
                "fn.test": {
                    "arg1": "boolean",
                },
                "->": [
                    {
                        "Ok_": {
                            "res1": "boolean",
                            "res2": "boolean"
                        }
                    }
                ]
            }
        ],
        [],
        0
    ),
    (
        [
            {
                "fn.test": {
                    "arg1": "boolean",
                    "arg2": "boolean"
                },
                "->": [
                    {
                        "Ok_": {
                            "res1": "boolean"
                        }
                    }
                ]
            }
        ],
        [
            {
                "fn.test": {
                    "arg1": "boolean",
                },
                "->": [
                    {
                        "Ok_": {
                            "res1": "boolean",
                        }
                    }
                ]
            }
        ],
        [
            'Backwards incompatible change(s) found:',
            '- Field \'arg2\' has been removed from struct \'fn.test\''
        ],
        1
    ),
    (
        [
            {
                "fn.test": {
                    "arg1": "boolean",
                },
                "->": [
                    {
                        "Ok_": {
                            "res1": "boolean"
                        }
                    }
                ]
            }
        ],
        [
            {
                "fn.test": {
                    "arg1": "boolean",
                    "arg2": "boolean"
                },
                "->": [
                    {
                        "Ok_": {
                            "res1": "boolean",
                        }
                    }
                ]
            }
        ],
        [
            'Backwards incompatible change(s) found:',
            '- New required field \'arg2\' has been added to struct \'fn.test\' on argument path'
        ],
        1
    ),
    (
        [
            {
                "fn.test": {
                    "arg1": "boolean",
                },
                "->": [
                    {
                        "Ok_": {
                            "res1": "boolean"
                        }
                    }
                ]
            }
        ],
        [
            {
                "fn.test": {
                    "arg1": "integer",
                },
                "->": [
                    {
                        "Ok_": {
                            "res1": "boolean",
                        }
                    }
                ]
            }
        ],
        [
            'Backwards incompatible change(s) found:',
            '- Field \'arg1\' in struct \'fn.test\' has changed type from \'boolean\' to \'integer\''
        ],
        1
    )     
]