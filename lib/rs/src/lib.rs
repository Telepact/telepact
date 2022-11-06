use std::{
    collections::HashMap,
    io::{BufReader, Read, Seek, Write},
    marker::PhantomData,
    rc::Rc,
};

pub mod parser;

use parser::*;

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

pub struct JapiProcessor {
    pub handler: fn(
        function_name: &str,
        headers: &Map<String, Value>,
        input: &Map<String, Value>,
    ) -> Result<Map<String, Value>, ApplicationError>,
    pub api_description: HashMap<String, Definition>,
}

pub struct JError {
    msg: String,
}

pub struct ApplicationError {}

pub struct InvalidRequest {}

pub type Output = Map<String, Value>;
type FunctionName = String;

pub enum ProcessError {
    Unknown,
    InvalidJson,
    JapiMessageNotArray,
    JapiMessageArrayTooFewElements,
    JapiMessageTypeNotString,
    JapiMessageHeaderNotObject,
    JapiMessageBodyNotObject,
    FunctionInputMissingFields(Vec<String>),
    ApplicationError(ApplicationError),
}

impl JapiProcessor {
    pub fn process<R: Read + Seek, W: Write>(
        &self,
        function_input_json: &mut R,
        function_output_json: &mut W,
    ) -> Result<(), JError> {
        let result = self._process(function_input_json);

        match result {
            Ok((function_name, output)) => {
                let msg_type = Value::String(format!("function.{}.output", function_name));
                let headers = Value::Object(Map::new());
                let body = Value::Object(output);

                let output_message = vec![msg_type, headers, body];

                to_writer(function_output_json, &output_message)
                    .map_err(|e| JError { msg: e.to_string() })?;
            }
            Err(e) => {
                let msg_type = Value::String(format!("error._ApplicationFailure"));
                let headers = Value::Object(Map::new());
                let body = Value::Object(Map::new());

                let japi_msg = vec![msg_type, headers, body];

                to_writer(function_output_json, &japi_msg)
                    .map_err(|e| JError { msg: e.to_string() })?;
            }
        }

        Ok(())
    }

    fn _process<R: Read + Seek>(
        &self,
        function_input_json: &mut R,
    ) -> Result<(FunctionName, Output), ProcessError> {
        let function_input: Value =
            from_reader(function_input_json).map_err(|e| ProcessError::InvalidJson)?;

        let payload_type = function_input
            .as_array()
            .ok_or(ProcessError::JapiMessageNotArray)?
            .get(0)
            .ok_or(ProcessError::JapiMessageArrayTooFewElements)?
            .as_str()
            .ok_or(ProcessError::JapiMessageTypeNotString)?;
        let function_name_re = Regex::new(r"^function\.([a-z][a-zA-Z0-9_]*)(.input)?").unwrap();
        let function_name_re_captures = function_name_re.captures(payload_type).unwrap();
        let function_name = function_name_re_captures
            .get(1)
            .ok_or(ProcessError::Unknown {})?
            .as_str();

        let headers = function_input
            .as_array()
            .ok_or(ProcessError::JapiMessageNotArray)?
            .get(1)
            .ok_or(ProcessError::JapiMessageArrayTooFewElements)?
            .as_object()
            .ok_or(ProcessError::JapiMessageHeaderNotObject)?;

        let input = function_input
            .as_array()
            .ok_or(ProcessError::JapiMessageNotArray)?
            .get(2)
            .ok_or(ProcessError::JapiMessageArrayTooFewElements)?
            .as_object()
            .ok_or(ProcessError::JapiMessageBodyNotObject)?;

        let function_def = self
            .api_description
            .get(&format!("function.{}", function_name))
            .ok_or(ProcessError::Unknown)?;
        let (input_def, output_def) = match function_def {
            Definition::Function {
                name,
                input_fields,
                output_fields,
            } => (input_fields, output_fields),
            _ => panic!(),
        };

        self.validate_struct(input_def, input)?;

        let result = (self.handler)(function_name, headers, input);

        return match result {
            Ok(o) => {
                self.validate_struct(output_def, &o)?;
                Ok((function_name.to_string(), o))
            }
            Err(a) => Err(ProcessError::ApplicationError(a)),
        };
    }

    fn validate_struct(
        &self,
        ref_struct: &HashMap<String, FieldDeclaration>,
        actual_struct: &Map<String, Value>,
    ) -> Result<(), ProcessError> {
        // TODO: validate struct
        let mut missing_fields: Vec<String> = Vec::new();
        for (name, field_declaration) in ref_struct {
            if !actual_struct.contains_key(name) {
                missing_fields.push(name.to_string());
            }
        }

        if !missing_fields.is_empty() {
            todo!();
        }
        return Ok(());
    }
}

#[cfg(test)]
mod tests {

    use std::{
        fs::File,
        io::{BufRead, Cursor},
        sync::Arc,
    };

    use serde_json::{from_str, json};

    use super::*;

    fn handle(
        function_name: &str,
        headers: &Map<String, Value>,
        input: &Map<String, Value>,
    ) -> Result<Output, ApplicationError> {
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

    #[derive(Debug)]
    struct Error {}

    #[test]
    fn check_cases() -> Result<(), Error> {
        let mut processor = JapiProcessor {
            handler: handle,
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

    // #[test]
    // fn it_works() {
    //     let mut processor = JapiProcessor {
    //         handler: MyHandler {},
    //         api_description: todo!(),
    //     };

    //     let input_json = r#"["function.add",{},{"x":2,"y":3}]"#.as_bytes();
    //     let ref mut reader = Cursor::new(input_json);

    //     let ref mut output_json = Vec::new();
    //     processor.process(reader, output_json);

    //     println!("{:?}", String::from_utf8(output_json.to_vec()).unwrap());

    //     assert_eq!(
    //         r#"["function.add.output",{},{"result":5.0}]"#.as_bytes(),
    //         output_json
    //     );
    // }

    #[test]
    fn desc_loads() {
        let ref json = r#"
        {
            "struct.Value": {
                "fields": {
                    "a": "integer"
                }
            },
            "function.add" : {
                "input.fields": {
                    "valueA": "struct.Value"
                },
                "output.fields": {}
            }
        }
        "#;
        let definitions: HashMap<String, Definition> = HashMap::new();
        let res = new_japi_description(&mut json.as_bytes());
        println!("result");
        let defs = match res {
            Ok(d) => d,
            Err(e) => {
                println!("{:?}", e.msg);
                HashMap::new()
            }
        };
        println!("{:?}", defs);
    }
}
