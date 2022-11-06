use std::{collections::HashMap, io::Cursor};
use std::fs;

use japi::{self, parser::Definition, Output, ApplicationError};
use serde_json::{json, Map, Value};

fn handle(
    function_name: &str,
    headers: &Map<String, Value>,
    input: &Map<String, Value>,
) -> Result<Output, ApplicationError> {
    return match function_name {
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


#[test]
fn desc_loads() {
    let json = fs::read_to_string("../../test/japi.json").unwrap();
    let defs = japi::parser::new_japi_description(&mut json.as_bytes()).unwrap();
    let processor = japi::JapiProcessor { handler: handle, api_description: defs };
    let input = r#"
    ["function.test",{"output":{"value":{"bool":false}}},{"value":{"bool":false}}]    
    "#;
    let expected_output = r#"
    ["function.test.output",{},{"value":{"bool":false}}]
    "#;
    let mut output = Vec::new();
    processor.process(&mut Cursor::new(input), &mut output);

    assert_eq!(
        expected_output.trim().to_string(),
        String::from_utf8(output).unwrap()
    )
}