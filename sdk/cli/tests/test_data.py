#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

compare_cases: list = [
    (
        "No change in function signature or result",
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
        "Adding new required field is compatible on result path",
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
        "Removing required argument is incompatible",
        [
            {
                "fn.test": {
                    "arg1": "boolean",
                    "arg2": "boolean"
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
                "fn.test": {
                    "arg1": "boolean",
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
            'Backwards incompatible change(s) found:',
            "- Field 'arg2' has been removed from struct 'fn.test'"
        ],
        1
    ),
    (
        "Adding new required argument is incompatible",
        [
            {
                "fn.test": {
                    "arg1": "boolean",
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
                "fn.test": {
                    "arg1": "boolean",
                    "arg2": "boolean"
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
            'Backwards incompatible change(s) found:',
            "- New required field 'arg2' has been added to struct 'fn.test' on argument path"
        ],
        1
    ),
    (
        "Changing argument type is incompatible",
        [
            {
                "fn.test": {
                    "arg1": "boolean",
                    "arg2": ["boolean"],
                    "arg3": {"string": "boolean"}
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
                "fn.test": {
                    "arg1": "integer",
                    "arg2": ["integer"],
                    "arg3": {"string": "integer"}
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
            'Backwards incompatible change(s) found:',
            "- Field 'arg1' in struct 'fn.test' has changed type from 'boolean' to 'integer'",
            "- Field 'arg2' in struct 'fn.test' has changed type from '['boolean']' to '['integer']'",
            "- Field 'arg3' in struct 'fn.test' has changed type from '{'string': 'boolean'}' to '{'string': 'integer'}'"
        ],
        1
    ),
    (
        "Changing result type is incompatible",
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
            "Backwards incompatible change(s) found:",
            "- Field 'res1' in struct 'fn.test.->.Ok_' has changed type from 'boolean' to 'integer'"
        ],
        1
    ),
    (
        "Changing struct field type is incompatible",
        [
            {
                "struct.S1": {
                    "field1": "boolean",
                    "field2": ["boolean"],
                    "field3": {"string": "boolean"}
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
                    "field1": "integer",
                    "field2": ["integer"],
                    "field3": {"string": "integer"}
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
            "- Field 'field1' in struct 'struct.S1' has changed type from 'boolean' to 'integer'",
            "- Field 'field2' in struct 'struct.S1' has changed type from '['boolean']' to '['integer']'",
            "- Field 'field3' in struct 'struct.S1' has changed type from '{'string': 'boolean'}' to '{'string': 'integer'}'"
        ],
        1
    ),
    (
        "Adding new required struct field is incompatible on argument path",
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
        "Adding new optional struct field is compatible",
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
        "Adding field to union tag is incompatible on argument path",
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
        "Removing field in union tag is incompatible",
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
        "Changing union tag field type is incompatible",
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
        "Removing union tag field is incompatible",
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
        "Adding new required union tag field is incompatible",
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
        "Adding new union tag is incompatible on result path",
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
        "Adding new union tag is compatible on argument path",
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
        "Removing union tag is incompatible",
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