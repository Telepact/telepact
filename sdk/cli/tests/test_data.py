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
            'Schema compatibility check failed with the following errors:',
            '- Field \'arg2\' has been removed from struct \'fn.test.fn.test\''
        ],
        1
    )    
]