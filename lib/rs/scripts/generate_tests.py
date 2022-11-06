from dataclasses import dataclass;

cases_filepath = "../../test/cases.txt"
test_filepath = "tests/cases.rs"

cases_file = open(cases_filepath, "r")
test_file = open(test_filepath, "w")

@dataclass
class Case:
    name: str
    input: str
    output: str

cases = []

current_test_name = None
counter = 0

for l in cases_file:
    line = l.rstrip()

    if line.startswith('"'):
        current_test_name = line[1:-1]
        counter = 1
    elif line == '':
        continue
    elif line.startswith('['):
        lines = line.split('|')
        input = lines[0]
        output = lines[1]

        case = Case('{}_{}'.format(current_test_name, counter), input, output)

        cases.append(case)

        counter += 1

test_file.write('''
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

''')

for case in cases:
    print(case)
    test_file.write("""
#[test]
fn test_{}() {{
    let json = fs::read_to_string("../../test/japi.json").unwrap();
    let defs = japi::parser::new_japi_description(&mut json.as_bytes()).unwrap();
    let processor = japi::JapiProcessor {{ handler: handle, api_description: defs }};
    let input = r#"
    {}
    "#.trim();
    let expected_output = r#"
    {}
    "#.trim();
    let mut output = Vec::new();
    processor.process(&mut Cursor::new(input), &mut output);

    assert_eq!(
        expected_output.to_string(),
        String::from_utf8(output).unwrap()
    )
}}

""".format(case.name, case.input, case.output)
    )
    
