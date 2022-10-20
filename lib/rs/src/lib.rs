use std::{
    collections::HashMap,
    io::{BufReader, Read, Seek, Write},
};

use regex::Regex;
use serde_json::{from_reader, json, to_writer, Map, Value};

pub trait Handler {
    fn handle(
        &self,
        function_name: &str,
        headers: &Map<String, Value>,
        input: &Map<String, Value>,
    ) -> Result<Map<String, Value>, ApplicationError>;
}

struct FieldDeclaration {
    t: TypeDeclaration,
    optional: bool,
}

enum Type {
    Boolean,
    Integer,
    Number,
    String,
    Array {
        nested_type: Box<Type>,
    },
    Object {
        nested_type: Box<Type>,
    },
    Struct {
        fields: Map<String, FieldDeclaration>,
    },
    Union {
        formats: Map<String, FieldDeclaration>,
    },
    Enum {
        allowed_values: Vec<String>,
    },
    Any,
}

struct TypeDeclaration {
    t: Type,
    nullable: bool,
}

pub struct JapiDescriptionParseError {
    msg: String,
}

pub struct JapiDescription {
    types: HashMap<String, Type>,
}

impl JapiDescription {
    pub fn new<R: Read>(japi_description_json: R) -> Result<(), crate::JapiDescriptionParseError> {
        let v: Value =
            from_reader(japi_description_json).map_err(|_| JapiDescriptionParseError {
                msg: "Invalid JSON".to_string(),
            })?;

        let root = v.as_object().ok_or(JapiDescriptionParseError {
            msg: "JSON document root must be an object".to_string(),
        })?;

        let mut typeDefsInc: HashMap<String, &Value> = HashMap::new();

        for (k, v) in root.iter() {
            let def_re = Regex::new(r"^([a-zA-Z0-9]+).([a-zA-Z_]+[a-zA-Z0-9_]*)$").unwrap();
            let def_re_captures = def_re.captures(k).unwrap();
            let japi_keyword = def_re_captures
                .get(0)
                .ok_or(JapiDescriptionParseError {
                    msg: "".to_string(),
                })?
                .as_str();
            let type_name = def_re_captures
                .get(1)
                .ok_or(JapiDescriptionParseError {
                    msg: "".to_string(),
                })?
                .as_str();
            let def = v.as_object().ok_or(JapiDescriptionParseError { msg: "All values in the JSON document root object must be objects".to_string() })?;

            match japi_keyword {
                "function" => {

                    let input_name = format!("{}.input", type_name);
                    let input_def = def.g

                    typeDefsInc.insert(input_name, v);
                }
                "struct" | "union" | "enum" | "error" => {
                    
                }
                _ => {
                    
                }
            }
        }

        return Ok(());
    }
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
