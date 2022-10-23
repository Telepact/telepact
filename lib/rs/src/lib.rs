use core::num::dec2flt::parse;
use std::{
    collections::HashMap,
    io::{BufReader, Read, Seek, Write},
};

use regex::Regex;
use serde::__private::de;
use serde_json::{from_reader, json, to_writer, Map, Value};

pub trait Handler {
    fn handle(
        &self,
        function_name: &str,
        headers: &Map<String, Value>,
        input: &Map<String, Value>,
    ) -> Result<Map<String, Value>, ApplicationError>;
}

struct FieldDeclaration<'a> {
    type_declaration: TypeDeclaration<'a>,
    optional: bool,
}

enum Type<'a> {
    Boolean,
    Integer,
    Number,
    String,
    Array {
        nested_type: TypeDeclaration<'a>,
    },
    Object {
        nested_type: TypeDeclaration<'a>,
    },
    Struct {
        fields: HashMap<String, FieldDeclaration<'a>>,
    },
    Union {
        cases: HashMap<String, FieldDeclaration<'a>>,
    },
    Enum {
        allowed_values: Vec<String>,
    },
    Any,
}

struct TypeDeclaration<'a> {
    t: &'a Type<'a>,
    nullable: bool,
}

enum Definition<'a> {
    Function {
        name: String,
        input_fields: HashMap<String, FieldDeclaration<'a>>,
        output_fields: HashMap<String, FieldDeclaration<'a>>,
    },
    Type {
        name: String,
        t: Type<'a>,
    },
}

pub struct JapiDescriptionParseError {
    msg: String,
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

fn parse_type<'a>(
    description_root: &'a Map<String, Value>,
    definitions: &'a mut HashMap<String, Definition<'a>>,
    type_declaration: &'a String,
) -> Result<(String, TypeDeclaration<'a>), JapiDescriptionParseError> {
    let type_def_re = Regex::new(r"^((boolean|integer|number|string)|((array|object)(<(.*)>)?)|((enum|struct|union)\.([a-zA-Z_]+[a-zA-Z0-9_])*))(\?)?$").unwrap();
    let type_def_re_captures = type_def_re.captures(type_declaration).unwrap();

    let is_nullable = type_def_re_captures.get(10).is_some();

    let standard_basic_type = type_def_re_captures.get(2).map(|capture| {
        let name = capture.as_str();
        let type_ = match name {
            "boolean" => Type::Boolean,
            "integer" => Type::Integer,
            "number" => Type::Number,
            "string" => Type::String,
        };
        (
            name.to_string(),
            TypeDeclaration {
                t: &type_,
                nullable: is_nullable,
            },
        )
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
                let default_nested_type_if_not_specified = (
                    "any".to_string(),
                    TypeDeclaration {
                        t: &Type::Any,
                        nullable: false,
                    },
                );
                specified_type.unwrap_or(default_nested_type_if_not_specified)
            })
            .map(|(nested_type_name, nested_type_declaration)| {
                let type_ = match name {
                    "array" => Type::Array {
                        nested_type: nested_type_declaration,
                    },
                    "object" => Type::Object {
                        nested_type: nested_type_declaration,
                    },
                };
                (
                    name.to_string(),
                    TypeDeclaration {
                        t: &type_,
                        nullable: is_nullable,
                    },
                )
            })
    });

    if standard_collection_type.is_some() {
        return Ok(standard_collection_type.unwrap()?);
    }

    let custom_type = type_def_re_captures.get(9).map(|capture| {
        let name = capture.as_str().to_string();
        if !definitions.contains_key(&name) {
            parse_def(description_root, definitions, &name);
        }

        let def = definitions.get(&name).unwrap();
        let _type = match def {
            Definition::Function {
                name,
                input_fields,
                output_fields,
            } => todo!(),
            Definition::Type { name, t } => t,
        };

        (
            name,
            TypeDeclaration {
                t: _type,
                nullable: is_nullable,
            },
        )
    });

    if custom_type.is_some() {
        return Ok(custom_type.unwrap());
    }

    return Err(JapiDescriptionParseError {
        msg: "Invalid type".to_string(),
    });
}

fn parse_field<'a>(
    description_root: &'a Map<String, Value>,
    definitions: &'a mut HashMap<String, Definition<'a>>,
    field_declaration: &'a String,
    type_declaration_val: &'a Value,
    is_for_union: bool,
) -> Result<(String, FieldDeclaration<'a>), JapiDescriptionParseError> {
    let type_declaration = type_declaration_val
        .as_str()
        .ok_or(JapiDescriptionParseError {
            msg: "Type declarations should be strings".to_string(),
        })?;

    // TODO: Need to parse generics out of this type definition
    let type_def_re = Regex::new(r"^(.*)(\?)?$").unwrap();
    let type_def_re_captures = type_def_re.captures(type_declaration).unwrap();

    let type_name = type_def_re_captures
        .get(1)
        .ok_or(JapiDescriptionParseError {
            msg: "Invalid function input type".to_string(),
        })?
        .as_str();

    let nullable = type_def_re_captures.get(2).is_some();

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

    if !definitions.contains_key(type_name) {
        let nested_desc = description_root.get(type_name);
        parse_def(description_root, definitions, &type_name.to_string())?;
    }

    let type_ = match definitions.get(type_name).unwrap() {
        Definition::Function {
            name,
            input_fields,
            output_fields,
        } => todo!(),
        Definition::Type { name, t } => t,
    };

    let type_declaration = TypeDeclaration {
        t: type_,
        nullable: nullable,
    };

    let field_declaration = FieldDeclaration {
        type_declaration: type_declaration,
        optional: optional,
    };

    return Ok((field_name.to_string(), field_declaration));
}

fn parse_def<'a>(
    description_root: &'a Map<String, Value>,
    definitions: &'a mut HashMap<String, Definition<'a>>,
    def_ref: &'a String,
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
                t: type_,
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
                t: type_,
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
                t: type_,
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

pub fn newJapiDescription<R: Read>(
    japi_description_json: R,
) -> Result<HashMap<String, Definition<'static>>, crate::JapiDescriptionParseError> {
    // Need to redo this method slightly.
    // Need to be able to better keep track of

    let v: Value = from_reader(japi_description_json).map_err(|_| JapiDescriptionParseError {
        msg: "Invalid JSON".to_string(),
    })?;

    let root = v.as_object().ok_or(JapiDescriptionParseError {
        msg: "JSON document root must be an object".to_string(),
    })?;

    let definitions: HashMap<String, Definition> = HashMap::new();

    for (def_ref, value) in root {
        if !definitions.contains_key(def_ref) {
            parse_def(root, &mut definitions, def_ref);
        }
    }

    return Ok(definitions);
}

pub struct JapiProcessor<H: Handler, A: Read> {
    handler: H,
    api_description: A,
}

pub struct Error {}

pub struct ApplicationError {}

impl<H: Handler, A: Read> JapiProcessor<H, A> {
    pub fn process<R: Read + Seek, W: Write>(
        &mut self,
        function_input_json: &mut R,
        function_output_json: &mut W,
    ) -> Result<(), crate::Error> {
        let function_input: Value = from_reader(function_input_json).map_err(|e| Error {})?;

        let payload_type = function_input
            .get(0)
            .ok_or(Error {})?
            .as_str()
            .ok_or(Error {})?;
        let function_name_re = Regex::new(r"^function\.([a-z][a-zA-Z0-9_]*)(.input)?").unwrap();
        let function_name_re_captures = function_name_re.captures(payload_type).unwrap();
        let function_name = function_name_re_captures.get(1).ok_or(Error {})?.as_str();

        let headers = function_input
            .get(1)
            .ok_or(Error {})?
            .as_object()
            .ok_or(Error {})?;

        let input = function_input
            .get(2)
            .ok_or(Error {})?
            .as_object()
            .ok_or(Error {})?;

        // TODO: validate against spec

        let result = self.handler.handle(function_name, headers, input);

        match result {
            Ok(output) => {
                // TODO: validate against spec
                let msg_type = Value::String(format!("function.{}.output", function_name));
                let headers = Value::Object(Map::new());
                let body = Value::Object(output);

                let output_message = vec![msg_type, headers, body];

                to_writer(function_output_json, &output_message).map_err(|e| Error {})?;
            }
            Err(e) => {
                let msg_type = Value::String(format!("error._ApplicationFailure"));
                let headers = Value::Object(Map::new());
                let body = Value::Object(Map::new());

                let japi_msg = vec![msg_type, headers, body];

                to_writer(function_output_json, &japi_msg).map_err(|e| Error {})?;
            }
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {

    use std::{
        fs::File,
        io::{BufRead, Cursor},
    };

    use serde_json::{from_str, json};

    use super::*;

    struct MyHandler {}

    impl Handler for MyHandler {
        fn handle(
            &self,
            function_name: &str,
            headers: &Map<String, Value>,
            input: &Map<String, Value>,
        ) -> Result<Map<String, Value>, ApplicationError> {
            return match function_name {
                "add" => {
                    let x = input
                        .get("x")
                        .ok_or(ApplicationError {})?
                        .as_f64()
                        .ok_or(ApplicationError {})?;
                    let y = input
                        .get("y")
                        .ok_or(ApplicationError {})?
                        .as_f64()
                        .ok_or(ApplicationError {})?;
                    let result = x + y;
                    let output = json!({ "result": result })
                        .as_object()
                        .ok_or(ApplicationError {})?
                        .to_owned();
                    Ok(output)
                }
                "test" => {
                    let output = if headers.contains_key("output") {
                        headers["output"]
                            .clone()
                            .as_object()
                            .ok_or(ApplicationError {})?
                            .to_owned()
                    } else {
                        json!({}).as_object().ok_or(ApplicationError {})?.to_owned()
                    };

                    Ok(output)
                }
                _ => Err(ApplicationError {}),
            };
        }
    }

    #[derive(Debug)]
    struct Error {}

    #[test]
    fn check_cases() -> Result<(), Error> {
        let mut processor = JapiProcessor {
            handler: MyHandler {},
            api_description: todo!(),
        };

        let cases_file = File::open("../../test/cases.txt").map_err(|_| Error {})?;
        let reader = BufReader::new(cases_file);

        let mut failures: Vec<String> = Vec::new();
        let mut test_namespace = "noNamespace".to_string();
        for line_result in reader.lines() {
            let line = line_result.map_err(|_| Error {})?;
            println!("{}", &line);
            if line.starts_with('"') {
                test_namespace = line.trim_matches('"').to_owned();
            } else if line.starts_with('[') {
                let split_line = line.split_once('|').ok_or(Error {})?;
                let japi_input_msg = split_line.0;
                let expected_japi_output_msg = split_line.1;

                let ref mut japi_output_msg_buf = Vec::new();

                let result =
                    processor.process(&mut Cursor::new(japi_input_msg), japi_output_msg_buf);

                let japi_output_msg = &match result {
                    Ok(_) => {
                        String::from_utf8(japi_output_msg_buf.to_owned()).map_err(|e| Error {})?
                    }
                    Err(_) => "Processor error".to_string(),
                }[..];

                if expected_japi_output_msg != japi_output_msg {
                    failures.push(format!(
                        "[{}] Failure for input: {}\n  Expected: {}\n  Actual: {}",
                        test_namespace, japi_input_msg, expected_japi_output_msg, japi_output_msg
                    ));
                }
            }
        }

        for failure in failures.iter() {
            println!("{}", failure);
        }

        assert!(failures.is_empty());

        Ok(())
    }

    #[test]
    fn it_works() {
        let mut processor = JapiProcessor {
            handler: MyHandler {},
            api_description: todo!(),
        };

        let input_json = r#"["function.add",{},{"x":2,"y":3}]"#.as_bytes();
        let ref mut reader = Cursor::new(input_json);

        let ref mut output_json = Vec::new();
        processor.process(reader, output_json);

        println!("{:?}", String::from_utf8(output_json.to_vec()).unwrap());

        assert_eq!(
            r#"["function.add.output",{},{"result":5.0}]"#.as_bytes(),
            output_json
        );
    }
}
