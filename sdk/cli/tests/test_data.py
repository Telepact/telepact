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
                },
                "->": [
                    {
                        "Ok_": {
                            "res1": "integer",
                        }
                    }
                ]
            }
        ],
        [
            'Backwards incompatible change(s) found:',
            '- Field \'res1\' in struct \'fn.test.->.Ok_\' has changed type from \'boolean\' to \'integer\''
        ],
        1
    ),
    (
        [
            {
                "struct.S1": {
                    "field1": "boolean"
                }
            },
            {
                "fn.test": {
                    "arg1": "struct.S1",
                },
                "->": [
                    {
                        "Ok_": {
                            "res1": "struct.S1"
                        }
                    }
                ]
            }
        ],
        [
            {
                "struct.S1": {
                    "field1": "integer"
                }
            },
            {
                "fn.test": {
                    "arg1": "struct.S1",
                },
                "->": [
                    {
                        "Ok_": {
                            "res1": "struct.S1"
                        }
                    }
                ]
            }
        ],
        [
            'Backwards incompatible change(s) found:',
            "- Field 'field1' in struct 'struct.S1' has changed type from 'boolean' to 'integer'"
        ],
        1
    ),
    (
        [
            {
                "struct.S1": {
                    "field1": "boolean"
                }
            },
            {
                "fn.test": {
                    "arg1": "struct.S1",
                },
                "->": [
                    {
                        "Ok_": {
                            "res1": "struct.S1"
                        }
                    }
                ]
            }
        ],
        [
            {
                "struct.S1": {
                    "field1": "boolean",
                    "field2": "boolean"
                }
            },
            {
                "fn.test": {
                    "arg1": "struct.S1",
                },
                "->": [
                    {
                        "Ok_": {
                            "res1": "struct.S1"
                        }
                    }
                ]
            }
        ],
        [
            'Backwards incompatible change(s) found:',
            "- New required field 'field2' has been added to struct 'struct.S1' on argument path"
        ],
        1
    ),
    (
        [
            {
                "struct.S1": {
                    "field1": "boolean"
                }
            },
            {
                "fn.test": {
                    "arg1": "struct.S1",
                },
                "->": [
                    {
                        "Ok_": {
                            "res1": "struct.S1"
                        }
                    }
                ]
            }
        ],
        [
            {
                "struct.S1": {
                    "field1": "boolean",
                    "field2!": "boolean"
                }
            },
            {
                "fn.test": {
                    "arg1": "struct.S1",
                },
                "->": [
                    {
                        "Ok_": {
                            "res1": "struct.S1"
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
                "union.U1": [
                    {
                        "Tag1": {
                            "field1": "boolean"
                        },
                    }
                ]
            },
            {
                "fn.test": {
                    "arg1": "union.U1",
                },
                "->": [
                    {
                        "Ok_": {
                            "res1": "union.U1"
                        }
                    }
                ]
            }
        ],
        [
            {
                "union.U1": [
                    {
                        "Tag1": {
                            "field1": "integer",
                        },
                    }
                ]
            },
            {
                "fn.test": {
                    "arg1": "union.U1",
                },
                "->": [
                    {
                        "Ok_": {
                            "res1": "union.U1"
                        }
                    }
                ]
            }
        ],
        [
            'Backwards incompatible change(s) found:',
            "- Field 'field1' in struct 'union.U1.Tag1' has changed type from 'boolean' to 'integer'"
        ],
        1
    ),
    (
        [
            {
                "union.U1": [
                    {
                        "Tag1": {
                            "field1": "boolean"
                        },
                    }
                ]
            },
            {
                "fn.test": {
                    "arg1": "union.U1",
                },
                "->": [
                    {
                        "Ok_": {
                            "res1": "union.U1"
                        }
                    }
                ]
            }
        ],
        [
            {
                "union.U1": [
                    {
                        "Tag1": {
                        },
                    }
                ]
            },
            {
                "fn.test": {
                    "arg1": "union.U1",
                },
                "->": [
                    {
                        "Ok_": {
                            "res1": "union.U1"
                        }
                    }
                ]
            }
        ],
        [
            'Backwards incompatible change(s) found:',
            "- Field 'field1' has been removed from struct 'union.U1.Tag1'"
        ],
        1
    ),
    (
        [
            {
                "union.U1": [
                    {
                        "Tag1": {
                            "field1": "boolean"
                        },
                    }
                ]
            },
            {
                "fn.test": {
                    "arg1": "union.U1",
                },
                "->": [
                    {
                        "Ok_": {
                            "res1": "union.U1"
                        }
                    }
                ]
            }
        ],
        [
            {
                "union.U1": [
                    {
                        "Tag1": {
                            "field1": "boolean",
                            "field2": "boolean"
                        },
                    }
                ]
            },
            {
                "fn.test": {
                    "arg1": "union.U1",
                },
                "->": [
                    {
                        "Ok_": {
                            "res1": "union.U1"
                        }
                    }
                ]
            }
        ],
        [
            'Backwards incompatible change(s) found:',
            "- New required field 'field2' has been added to struct 'union.U1.Tag1' on argument path"
        ],
        1
    ),
    (
        [
            {
                "union.U1": [
                    {
                        "Tag1": {
                            "field1": "boolean"
                        },
                    }
                ]
            },
            {
                "fn.test": {
                    "arg1": "union.U1",
                },
                "->": [
                    {
                        "Ok_": {
                            "res1": "union.U1"
                        }
                    }
                ]
            }
        ],
        [
            {
                "union.U1": [
                    {
                        "Tag1": {
                            "field1": "boolean",
                        },
                    },
                    {
                        "Tag2": {}
                    }
                ]
            },
            {
                "fn.test": {
                    "arg1": "union.U1",
                },
                "->": [
                    {
                        "Ok_": {
                            "res1": "union.U1"
                        }
                    }
                ]
            }
        ],
        [
            'Backwards incompatible change(s) found:',
            "- New tag 'Tag2' has been added to union 'union.U1' on result path"
        ],
        1
    ),
    (
        [
            {
                "union.U1": [
                    {
                        "Tag1": {
                            "field1": "boolean"
                        },
                    }
                ]
            },
            {
                "fn.test": {
                    "arg1": "union.U1",
                },
                "->": [
                    {
                        "Ok_": {
                        }
                    }
                ]
            }
        ],
        [
            {
                "union.U1": [
                    {
                        "Tag1": {
                            "field1": "boolean",
                        },
                    },
                    {
                        "Tag2": {}
                    }
                ]
            },
            {
                "fn.test": {
                    "arg1": "union.U1",
                },
                "->": [
                    {
                        "Ok_": {
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
                "union.U1": [
                    {
                        "Tag1": {
                            "field1": "boolean"
                        },                      
                    },
                    {
                        "Tag2": {}
                    }
                ]
            },
            {
                "fn.test": {
                    "arg1": "union.U1",
                },
                "->": [
                    {
                        "Ok_": {
                            "res1": "union.U1"
                        }
                    }
                ]
            }
        ],
        [
            {
                "union.U1": [
                    {
                        "Tag1": {
                            "field1": "boolean",
                        },
                    },

                ]
            },
            {
                "fn.test": {
                    "arg1": "union.U1",
                },
                "->": [
                    {
                        "Ok_": {
                            "res1": "union.U1"
                        }
                    }
                ]
            }
        ],
        [
            'Backwards incompatible change(s) found:',
            "- Tag 'Tag2' has been removed from union 'union.U1'"
        ],
        1
    ),
]