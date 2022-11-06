use std::collections::HashMap;
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
    let res = japi::parser::new_japi_description(&mut json.as_bytes());
    println!("result");
    let defs = match res {
        Ok(d) => d,
        Err(e) => {
            println!("{:?}", e.msg);
            HashMap::new()
        }
    };
    println!("{:?}", defs);

    let processor = japi::JapiProcessor { handler: handle, api_description: defs };
}