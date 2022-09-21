use std::io::{Read, Seek, Write, BufReader};

use regex::Regex;
use serde_json::{from_reader, to_writer, Map, Value, json};

pub trait Handler {
    fn handle(
        &self,
        function_name: &str,
        headers: &Map<String, Value>,
        input: &Map<String, Value>,
    ) -> Result<Map<String, Value>, ApplicationError>;
}

pub struct JapiProcessor<H: Handler> {
    handler: H,
}

pub struct Error {}

pub struct ApplicationError {}

impl<H: Handler> JapiProcessor<H> {
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
                let output_type = Value::String(format!("function.{}.output", function_name));
                let headers = Value::Object(Map::new());
                let wrapped_output = Value::Object(output);

                let output_message = vec![
                    output_type,
                    headers,
                    wrapped_output
                ];

                to_writer(function_output_json, &output_message);
            }
            Err(e) => {
                // TODO
            }
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {

    use std::io::Cursor;

    use serde_json::json;

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
                        .ok_or(ApplicationError {})?.to_owned();
                    Ok(output)
                }
                _ => Err(ApplicationError {}),
            };
        }
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
