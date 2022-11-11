use std::{collections::HashMap, io::Read, rc::Rc};

use regex::Regex;
use serde_json::{from_reader, Map, Value};

#[derive(Debug)]
pub struct FieldDeclaration {
    pub type_declaration: TypeDeclaration,
    pub optional: bool,
}

#[derive(Debug)]
pub enum Type {
    Boolean,
    Integer,
    Number,
    String,
    Array {
        nested_type: TypeDeclaration,
    },
    Object {
        nested_type: TypeDeclaration,
    },
    Struct {
        fields: HashMap<String, FieldDeclaration>,
    },
    Union {
        cases: HashMap<String, FieldDeclaration>,
    },
    Enum {
        allowed_values: Vec<String>,
    },
    Any,
}

#[derive(Debug)]
pub struct TypeDeclaration {
    pub t: Rc<Type>,
    pub nullable: bool,
}

#[derive(Debug)]
pub enum Definition {
    Function {
        name: String,
        input_fields: HashMap<String, FieldDeclaration>,
        output_fields: HashMap<String, FieldDeclaration>,
    },
    Type {
        name: String,
        t: Rc<Type>,
    },
}

#[derive(Debug)]
pub struct JapiDescriptionParseError {
    pub msg: String,
}

fn split_japi_definition_name(
    name: &String,
) -> Result<(String, String), JapiDescriptionParseError> {
    let def_re =
        Regex::new(r"^(struct|union|enum|error|function|event).([a-zA-Z_]+[a-zA-Z0-9_]*)$")
            .unwrap();
    let def_re_captures = def_re.captures(name).unwrap();
    let japi_keyword = def_re_captures
        .get(1)
        .ok_or(JapiDescriptionParseError {
            msg: "Invalid definition".to_string(),
        })?
        .as_str();
    let name = def_re_captures
        .get(2)
        .ok_or(JapiDescriptionParseError {
            msg: "Invalid definition".to_string(),
        })?
        .as_str();

    return Ok((japi_keyword.to_string(), name.to_string()));
}

fn parse_type(
    description_root: &Map<String, Value>,
    definitions: &mut HashMap<String, Definition>,
    type_declaration: &'_ String,
) -> Result<TypeDeclaration, JapiDescriptionParseError> {
    let type_def_re = Regex::new(r"^((boolean|integer|number|string|any)|((array|object)(<(.*)>)?)|((enum|struct|union)\.([a-zA-Z_]+[a-zA-Z0-9_])*))(\?)?$").unwrap();
    let type_def_re_captures =
        type_def_re
            .captures(type_declaration)
            .ok_or(JapiDescriptionParseError {
                msg: format!("Could not parse type {}", type_declaration),
            })?;

    let is_nullable = type_def_re_captures.get(10).is_some();

    let standard_basic_type = type_def_re_captures.get(2).map(|capture| {
        let name = capture.as_str();
        let type_ = match name {
            "boolean" => Type::Boolean,
            "integer" => Type::Integer,
            "number" => Type::Number,
            "string" => Type::String,
            "any" => Type::Any,
            _ => panic!(),
        };
        TypeDeclaration {
            t: Rc::new(type_),
            nullable: is_nullable,
        }
    });

    if standard_basic_type.is_some() {
        return Ok(standard_basic_type.unwrap());
    }

    let standard_collection_type = type_def_re_captures.get(4).map(|capture| {
        let name = capture.as_str();
        type_def_re_captures
            .get(6)
            .map(|capture| {
                let nested_name = capture.as_str().to_string();
                parse_type(description_root, definitions, &nested_name)
            })
            .transpose()
            .map(|specified_type| {
                let default_nested_type_if_not_specified = TypeDeclaration {
                    t: Rc::new(Type::Any),
                    nullable: false,
                };
                specified_type.unwrap_or(default_nested_type_if_not_specified)
            })
            .map(|nested_type_declaration| {
                let type_ = match name {
                    "array" => Type::Array {
                        nested_type: nested_type_declaration,
                    },
                    "object" => Type::Object {
                        nested_type: nested_type_declaration,
                    },
                    _ => panic!(),
                };

                TypeDeclaration {
                    t: Rc::new(type_),
                    nullable: is_nullable,
                }
            })
    });

    if standard_collection_type.is_some() {
        return Ok(standard_collection_type.unwrap()?);
    }

    let custom_type = type_def_re_captures.get(7).map(|capture| {
        let _name = capture.as_str().to_string();
        if !definitions.contains_key(&_name) {
            parse_def(description_root, definitions, &_name)?;
        }

        let def = definitions.get(&_name).unwrap();
        match def {
            Definition::Function {
                name: _,
                input_fields: _,
                output_fields: _,
            } => todo!(),
            Definition::Type { name: _, t } => Ok(TypeDeclaration {
                t: Rc::clone(t),
                nullable: is_nullable,
            }),
            _ => Err(JapiDescriptionParseError {
                msg: "Could not find custom type reference".to_string(),
            }),
        }
    });

    if custom_type.is_some() {
        return Ok(custom_type.unwrap()?);
    }

    return Err(JapiDescriptionParseError {
        msg: "Invalid type".to_string(),
    });
}

fn parse_field(
    description_root: &Map<String, Value>,
    definitions: &mut HashMap<String, Definition>,
    field_declaration: &String,
    type_declaration_val: &Value,
    is_for_union: bool,
) -> Result<(String, FieldDeclaration), JapiDescriptionParseError> {
    let field_def_re = Regex::new(r"^([a-zA-Z_]+[a-zA-Z0-9_]*)(!)?$").unwrap();
    let field_def_re_captures = field_def_re.captures(field_declaration).unwrap();

    let field_name = field_def_re_captures
        .get(1)
        .ok_or(JapiDescriptionParseError {
            msg: "Invalid function input field".to_string(),
        })?
        .as_str();

    let optional = field_def_re_captures.get(2).is_some();

    if (optional && is_for_union) {
        return Err(JapiDescriptionParseError {
            msg: "Union keys cannot be marked as optional".to_string(),
        });
    }

    let type_declaration_str = type_declaration_val
        .as_str()
        .ok_or(JapiDescriptionParseError {
            msg: "Type declarations should be strings".to_string(),
        })?;

    let type_declaration = parse_type(
        description_root,
        definitions,
        &type_declaration_str.to_string(),
    )?;

    let field_declaration = FieldDeclaration {
        type_declaration: type_declaration,
        optional: optional,
    };

    return Ok((field_name.to_string(), field_declaration));
}

fn parse_def(
    description_root: &Map<String, Value>,
    definitions: &mut HashMap<String, Definition>,
    def_ref: &String,
) -> Result<(), JapiDescriptionParseError> {
    let desc = description_root
        .get(def_ref)
        .ok_or(JapiDescriptionParseError {
            msg: format!("Could not find definition for {}", def_ref),
        })?;

    let (japi_keyword, def_name) = split_japi_definition_name(def_ref)?;

    let def = match &japi_keyword[..] {
        "function" => {
            let input_def = desc
                .get("input.fields")
                .ok_or(JapiDescriptionParseError {
                    msg: "Function definition must have \"input.fields\" key".to_string(),
                })?
                .as_object()
                .ok_or(JapiDescriptionParseError {
                    msg: "Function definition \"input.fields\" key must point to an object"
                        .to_string(),
                })?;

            let mut input_fields: HashMap<String, FieldDeclaration> = HashMap::new();
            for (field_declaration, type_declaration_val) in input_def {
                let (field_name, field_declaration) = parse_field(
                    description_root,
                    definitions,
                    field_declaration,
                    type_declaration_val,
                    false,
                )?;
                input_fields.insert(field_name, field_declaration);
            }

            let output_def = desc
                .get("output.fields")
                .ok_or(JapiDescriptionParseError {
                    msg: "Function definition must have \"output.fields\" key".to_string(),
                })?
                .as_object()
                .ok_or(JapiDescriptionParseError {
                    msg: "Function definition \"output.fields\" key must point to an object"
                        .to_string(),
                })?;

            let mut output_fields: HashMap<String, FieldDeclaration> = HashMap::new();
            for (field_declaration, type_declaration_val) in output_def {
                let (field_name, field_declaration) = parse_field(
                    description_root,
                    definitions,
                    field_declaration,
                    type_declaration_val,
                    false,
                )?;
                output_fields.insert(field_name, field_declaration);
            }

            Definition::Function {
                name: def_name,
                input_fields: input_fields,
                output_fields: output_fields,
            }
        }
        "struct" => {
            let struct_def = desc
                .get("fields")
                .ok_or(JapiDescriptionParseError {
                    msg: "struct definition must have \"fields\" key".to_string(),
                })?
                .as_object()
                .ok_or(JapiDescriptionParseError {
                    msg: "struct definition \"fields\" key must point to an object".to_string(),
                })?;

            let mut fields: HashMap<String, FieldDeclaration> = HashMap::new();
            for (field_declaration, type_declaration_val) in struct_def {
                let (field_name, field_declaration) = parse_field(
                    description_root,
                    definitions,
                    field_declaration,
                    type_declaration_val,
                    false,
                )?;
                fields.insert(field_name, field_declaration);
            }

            let type_ = Type::Struct { fields: fields };

            Definition::Type {
                name: def_name,
                t: Rc::new(type_),
            }
        }
        "union" => {
            let union_def = desc
                .get("cases")
                .ok_or(JapiDescriptionParseError {
                    msg: "union definition must have \"cases\" key".to_string(),
                })?
                .as_object()
                .ok_or(JapiDescriptionParseError {
                    msg: "union definition \"cases\" key must point to an object".to_string(),
                })?;

            let mut fields: HashMap<String, FieldDeclaration> = HashMap::new();
            for (field_declaration, type_declaration_val) in union_def {
                let (field_name, field_declaration) = parse_field(
                    description_root,
                    definitions,
                    field_declaration,
                    type_declaration_val,
                    true,
                )?;
                fields.insert(field_name, field_declaration);
            }

            let type_ = Type::Union { cases: fields };

            Definition::Type {
                name: def_name,
                t: Rc::new(type_),
            }
        }
        "enum" => {
            let enum_def = desc
                .get("values")
                .ok_or(JapiDescriptionParseError {
                    msg: "enum definition must have \"values\" key".to_string(),
                })?
                .as_array()
                .ok_or(JapiDescriptionParseError {
                    msg: "enum definition \"values\" key must point to an array".to_string(),
                })?;

            let mut values: Vec<String> = Vec::new();
            for value_val in enum_def {
                let value = value_val.as_str().ok_or(JapiDescriptionParseError {
                    msg: "enum definition \"values\" key must point to an array of strings"
                        .to_string(),
                })?;

                values.push(value.to_string());
            }

            let type_ = Type::Enum {
                allowed_values: values,
            };

            Definition::Type {
                name: def_name,
                t: Rc::new(type_),
            }
        }
        _ => {
            return Err(JapiDescriptionParseError {
                msg: format!("Unrecognized japi keyword {}", japi_keyword),
            });
        }
    };

    definitions.insert(def_ref.to_string(), def);

    return Ok(());
}

pub fn new_japi_description<R: Read>(
    japi_description_json: &mut R,
) -> Result<HashMap<String, Definition>, crate::JapiDescriptionParseError> {
    let mut descriptions: HashMap<String, Definition> = HashMap::new();

    let v: Value = from_reader(japi_description_json).map_err(|_| JapiDescriptionParseError {
        msg: "Invalid JSON".to_string(),
    })?;

    let root = v.as_object().ok_or(JapiDescriptionParseError {
        msg: "JSON document root must be an object".to_string(),
    })?;

    for (def_ref, _) in root {
        if !descriptions.contains_key(def_ref) {
            parse_def(root, &mut descriptions, def_ref)?;
        }
    }

    return Ok(descriptions);
}
