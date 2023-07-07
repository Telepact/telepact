use std::{
    borrow::Borrow,
    collections::HashMap,
    io::{BufReader, Read, Seek, Write},
    marker::PhantomData,
    rc::Rc,
};

pub mod parser;

use parser::*;

use regex::Regex;
use serde::__private::de;
use serde_json::{from_reader, json, to_writer, Error, Map, Value};

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

#[derive(Debug)]
pub struct ApplicationError {}

pub struct InvalidRequest {}

pub type Output = Map<String, Value>;
type FunctionName = String;

#[derive(Debug)]
pub enum FieldError {
    StructMissingFields(String, Vec<String>),
    StructHasExtraFields(String, Vec<String>),
    UnionDoesNotHaveOnlyOneField(String),
    UnknownUnionField(String, String),
    InvalidEnumValue(String),
    FieldWasNotExpectedType(String, &'static str),
    NullInvalidForNonNullType(String),
    IntegerInvalidForBooleanType(String),
    NumberInvalidForBooleanType(String),
    StringInvalidForBooleanType(String),
    ArrayInvalidForBooleanType(String),
    ObjectInvalidForBooleanType(String),
    BooleanInvalidForIntegerType(String),
    NumberInvalidForIntegerType(String),
    StringInvalidForIntegerType(String),
    ArrayInvalidForIntegerType(String),
    ObjectInvalidForIntegerType(String),
    BooleanInvalidForNumberType(String),
    StringInvalidForNumberType(String),
    ArrayInvalidForNumberType(String),
    ObjectInvalidForNumberType(String),
    BooleanInvalidForStringType(String),
    IntegerInvalidForStringType(String),
    NumberInvalidForStringType(String),
    ArrayInvalidForStringType(String),
    ObjectInvalidForStringType(String),
    BooleanInvalidForArrayType(String),
    IntegerInvalidForArrayType(String),
    NumberInvalidForArrayType(String),
    StringInvalidForArrayType(String),
    ObjectInvalidForArrayType(String),
    BooleanInvalidForObjectType(String),
    IntegerInvalidForObjectType(String),
    NumberInvalidForObjectType(String),
    StringInvalidForObjectType(String),
    ArrayInvalidForObjectType(String),
    BooleanInvalidForStructType(String),
    IntegerInvalidForStructType(String),
    NumberInvalidForStructType(String),
    StringInvalidForStructType(String),
    ArrayInvalidForStructType(String),
    BooleanInvalidForUnionType(String),
    IntegerInvalidForUnionType(String),
    NumberInvalidForUnionType(String),
    StringInvalidForUnionType(String),
    ArrayInvalidForUnionType(String),
    BooleanInvalidForEnumType(String),
    IntegerInvalidForEnumType(String),
    NumberInvalidForEnumType(String),
    ArrayInvalidForEnumType(String),
    ObjectInvalidForEnumType(String),
    NonNullInvalidForNullType(String),
}

#[derive(Debug)]
pub enum ProcessError {
    Unknown,
    InvalidJson(Error),
    JapiMessageNotArray,
    JapiMessageArrayTooFewElements,
    JapiMessageTypeNotString,
    JapiMessageHeaderNotObject,
    JapiMessageBodyNotObject,
    FunctionInputMissingFields(Vec<String>),
    ApplicationError(ApplicationError),
    InvalidInput(FieldError),
    InvalidOutput(FieldError),
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
                let headers = Value::Object(Map::new());

                println!("error: {:?}", e);

                let (msg_type, body) = match e {
                    ProcessError::InvalidInput(e2) => match e2 {
                        FieldError::NullInvalidForNonNullType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"NullInvalidForNonNullType".to_string()),
                        ),
                        FieldError::IntegerInvalidForBooleanType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(
                                &field,
                                &"IntegerInvalidForBooleanType".to_string(),
                            ),
                        ),
                        FieldError::NumberInvalidForBooleanType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"NumberInvalidForBooleanType".to_string()),
                        ),
                        FieldError::StringInvalidForBooleanType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"StringInvalidForBooleanType".to_string()),
                        ),
                        FieldError::ArrayInvalidForBooleanType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"ArrayInvalidForBooleanType".to_string()),
                        ),
                        FieldError::ObjectInvalidForBooleanType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"ObjectInvalidForBooleanType".to_string()),
                        ),
                        FieldError::BooleanInvalidForIntegerType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(
                                &field,
                                &"BooleanInvalidForIntegerType".to_string(),
                            ),
                        ),
                        FieldError::NumberInvalidForIntegerType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"NumberInvalidForIntegerType".to_string()),
                        ),
                        FieldError::StringInvalidForIntegerType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"StringInvalidForIntegerType".to_string()),
                        ),
                        FieldError::ArrayInvalidForIntegerType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"ArrayInvalidForIntegerType".to_string()),
                        ),
                        FieldError::ObjectInvalidForIntegerType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"ObjectInvalidForIntegerType".to_string()),
                        ),
                        FieldError::BooleanInvalidForNumberType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"BooleanInvalidForNumberType".to_string()),
                        ),
                        FieldError::StringInvalidForNumberType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"StringInvalidForNumberType".to_string()),
                        ),
                        FieldError::ArrayInvalidForNumberType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"ArrayInvalidForNumberType".to_string()),
                        ),
                        FieldError::ObjectInvalidForNumberType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"ObjectInvalidForNumberType".to_string()),
                        ),

                        FieldError::BooleanInvalidForStringType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"BooleanInvalidForStringType".to_string()),
                        ),
                        FieldError::IntegerInvalidForStringType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"NumberInvalidForStringType".to_string()),
                        ),
                        FieldError::NumberInvalidForStringType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"NumberInvalidForStringType".to_string()),
                        ),
                        FieldError::ArrayInvalidForStringType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"ArrayInvalidForStringType".to_string()),
                        ),
                        FieldError::ObjectInvalidForStringType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"ObjectInvalidForStringType".to_string()),
                        ),

                        FieldError::BooleanInvalidForArrayType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"BooleanInvalidForArrayType".to_string()),
                        ),
                        FieldError::IntegerInvalidForArrayType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"NumberInvalidForArrayType".to_string()),
                        ),
                        FieldError::NumberInvalidForArrayType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"NumberInvalidForArrayType".to_string()),
                        ),
                        FieldError::StringInvalidForArrayType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"StringInvalidForArrayType".to_string()),
                        ),
                        FieldError::ObjectInvalidForArrayType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"ObjectInvalidForArrayType".to_string()),
                        ),

                        FieldError::BooleanInvalidForObjectType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"BooleanInvalidForObjectType".to_string()),
                        ),
                        FieldError::IntegerInvalidForObjectType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"NumberInvalidForObjectType".to_string()),
                        ),
                        FieldError::NumberInvalidForObjectType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"NumberInvalidForObjectType".to_string()),
                        ),
                        FieldError::StringInvalidForObjectType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"StringInvalidForObjectType".to_string()),
                        ),
                        FieldError::ArrayInvalidForObjectType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"ArrayInvalidForObjectType".to_string()),
                        ),
                        FieldError::BooleanInvalidForStructType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"BooleanInvalidForStructType".to_string()),
                        ),
                        FieldError::IntegerInvalidForStructType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"NumberInvalidForStructType".to_string()),
                        ),
                        FieldError::NumberInvalidForStructType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"NumberInvalidForStructType".to_string()),
                        ),
                        FieldError::StringInvalidForStructType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"StringInvalidForStructType".to_string()),
                        ),
                        FieldError::ArrayInvalidForStructType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"ArrayInvalidForStructType".to_string()),
                        ),
                        FieldError::BooleanInvalidForUnionType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"BooleanInvalidForUnionType".to_string()),
                        ),
                        FieldError::IntegerInvalidForUnionType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"NumberInvalidForUnionType".to_string()),
                        ),
                        FieldError::NumberInvalidForUnionType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"NumberInvalidForUnionType".to_string()),
                        ),
                        FieldError::StringInvalidForUnionType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"StringInvalidForUnionType".to_string()),
                        ),
                        FieldError::ArrayInvalidForUnionType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"ArrayInvalidForUnionType".to_string()),
                        ),
                        FieldError::BooleanInvalidForEnumType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"BooleanInvalidForEnumType".to_string()),
                        ),
                        FieldError::IntegerInvalidForEnumType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"NumberInvalidForEnumType".to_string()),
                        ),
                        FieldError::NumberInvalidForEnumType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"NumberInvalidForEnumType".to_string()),
                        ),
                        FieldError::ArrayInvalidForEnumType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"ArrayInvalidForEnumType".to_string()),
                        ),
                        FieldError::ObjectInvalidForEnumType(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"ObjectInvalidForEnumType".to_string()),
                        ),
                        FieldError::InvalidEnumValue(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(&field, &"UnknownEnumValue".to_string()),
                        ),
                        FieldError::StructMissingFields(namespace, fields) => {
                            let errors: Vec<(String, String)> = fields
                                .iter()
                                .map(|f| {
                                    (
                                        format!("{}.{}", namespace, f),
                                        "RequiredStructFieldMissing".to_string(),
                                    )
                                })
                                .collect();
                            (
                                Value::String(format!("error._InvalidRequestBody")),
                                self._invalid_fields(errors),
                            )
                        }
                        FieldError::StructHasExtraFields(namespace, fields) => {
                            let errors: Vec<(String, String)> = fields
                                .iter()
                                .map(|f| {
                                    (
                                        format!("{}.{}", namespace, f),
                                        "UnknownStructField".to_string(),
                                    )
                                })
                                .collect();
                            (
                                Value::String(format!("error._InvalidRequestBody")),
                                self._invalid_fields(errors),
                            )
                        }
                        FieldError::UnionDoesNotHaveOnlyOneField(field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(
                                &field,
                                &"UnionDoesNotHaveExactlyOneField".to_string(),
                            ),
                        ),
                        FieldError::UnknownUnionField(namespace, field) => (
                            Value::String(format!("error._InvalidRequestBody")),
                            self._invalid_field(
                                &format!("{}.{}", namespace, field),
                                &"UnknownUnionField".to_string(),
                            ),
                        ),
                        _ => (
                            Value::String(format!("error._ApplicationFailure")),
                            Value::Object(Map::new()),
                        ),
                    },
                    ProcessError::InvalidOutput(_) => (
                        Value::String(format!("error._InvalidResponseBody")),
                        Value::Object(Map::new()),
                    ),
                    _ => (
                        Value::String(format!("error._ApplicationFailure")),
                        Value::Object(Map::new()),
                    ),
                };

                let japi_msg = vec![msg_type, headers, body];

                to_writer(function_output_json, &japi_msg)
                    .map_err(|e| JError { msg: e.to_string() })?;
            }
        }

        Ok(())
    }

    fn _invalid_field(&self, field: &String, reason: &String) -> Value {
        return self._invalid_fields(vec![(field.to_owned(), reason.to_owned())]);
    }

    fn _invalid_fields(&self, errors: Vec<(String, String)>) -> Value {
        let jsonErrors: Vec<Value> = errors
            .into_iter()
            .map(|(field, reason)| {
                json!({
                    "field": field,
                    "reason": reason
                })
            })
            .collect();
        return json!({ "cases": jsonErrors });
    }

    fn _process<R: Read + Seek>(
        &self,
        function_input_json: &mut R,
    ) -> Result<(FunctionName, Output), ProcessError> {
        let function_input: Value =
            from_reader(function_input_json).map_err(|e| ProcessError::InvalidJson(e))?;

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

        self.validate_struct(&"input".to_string(), input_def, input)
            .map_err(|e| ProcessError::InvalidInput(e))?;

        let result = (self.handler)(function_name, headers, input);

        return match result {
            Ok(o) => {
                self.validate_struct(&"output".to_string(), output_def, &o)
                    .map_err(|e| ProcessError::InvalidOutput(e))?;
                Ok((function_name.to_string(), o))
            }
            Err(a) => Err(ProcessError::ApplicationError(a)),
        };
    }

    fn validate_struct(
        &self,
        namespace: &String,
        ref_struct: &HashMap<String, FieldDeclaration>,
        actual_struct: &Map<String, Value>,
    ) -> Result<(), FieldError> {
        let mut missing_fields: Vec<String> = Vec::new();
        for (name, field_declaration) in ref_struct {
            if !actual_struct.contains_key(name) && !field_declaration.optional {
                missing_fields.push(name.to_string());
            }
        }

        if !missing_fields.is_empty() {
            return Err(FieldError::StructMissingFields(
                namespace.to_string(),
                missing_fields,
            ));
        }

        let mut extra_fields: Vec<String> = Vec::new();
        for (name, _) in actual_struct {
            if !ref_struct.contains_key(name) {
                extra_fields.push(name.to_string());
            }
        }

        if !extra_fields.is_empty() {
            return Err(FieldError::StructHasExtraFields(
                namespace.to_string(),
                extra_fields,
            ));
        }

        for (name, field) in actual_struct {
            let ref_field = ref_struct
                .get(name)
                .ok_or(FieldError::StructHasExtraFields(
                    namespace.to_string(),
                    vec![name.to_string()],
                ))?;
            self.validate_type(
                &format!("{}.{}", namespace, name).to_string(),
                &ref_field.type_declaration,
                field,
            )?;
        }

        return Ok(());
    }

    fn validate_union(
        &self,
        namespace: &String,
        ref_struct: &HashMap<String, FieldDeclaration>,
        actual_struct: &Map<String, Value>,
    ) -> Result<(), FieldError> {
        if actual_struct.len() != 1 {
            return Err(FieldError::UnionDoesNotHaveOnlyOneField(
                namespace.to_string(),
            ));
        }

        let (name, field_value) = actual_struct.iter().next().unwrap();

        let ref_field = ref_struct.get(name).ok_or(FieldError::UnknownUnionField(
            namespace.to_string(),
            name.to_string(),
        ))?;
        self.validate_type(
            &format!("{}.{}", namespace, name).to_string(),
            &ref_field.type_declaration,
            field_value,
        )?;

        return Ok(());
    }

    fn validate_type(
        &self,
        field_name: &String,
        type_declaration: &TypeDeclaration,
        value: &Value,
    ) -> Result<(), FieldError> {
        match value {
            Value::Null => {
                if !type_declaration.nullable {
                    Err(FieldError::NullInvalidForNonNullType(
                        field_name.to_string(),
                    ))
                } else {
                    Ok(())
                }
            }
            _ => {
                let expected_type = &*type_declaration.t;
                match expected_type {
                    Type::Boolean => match value {
                        Value::Bool(_) => Ok(()),
                        Value::Number(_) => Err(FieldError::NumberInvalidForBooleanType(
                            field_name.to_string(),
                        )),
                        Value::String(_) => Err(FieldError::StringInvalidForBooleanType(
                            field_name.to_string(),
                        )),
                        Value::Array(_) => Err(FieldError::ArrayInvalidForBooleanType(
                            field_name.to_string(),
                        )),
                        Value::Object(_) => Err(FieldError::ObjectInvalidForBooleanType(
                            field_name.to_string(),
                        )),
                        Value::Null => {
                            if !type_declaration.nullable {
                                Err(FieldError::NullInvalidForNonNullType(
                                    field_name.to_string(),
                                ))
                            } else {
                                Ok(())
                            }
                        }
                    },
                    Type::Integer => match value {
                        Value::Bool(_) => Err(FieldError::BooleanInvalidForIntegerType(
                            field_name.to_string(),
                        )),
                        Value::Number(_) => {
                            if !value.is_i64() {
                                Err(FieldError::NumberInvalidForIntegerType(
                                    field_name.to_string(),
                                ))
                            } else {
                                Ok(())
                            }
                        }
                        Value::String(_) => Err(FieldError::StringInvalidForIntegerType(
                            field_name.to_string(),
                        )),
                        Value::Array(_) => Err(FieldError::ArrayInvalidForIntegerType(
                            field_name.to_string(),
                        )),
                        Value::Object(_) => Err(FieldError::ObjectInvalidForIntegerType(
                            field_name.to_string(),
                        )),
                        Value::Null => {
                            if !type_declaration.nullable {
                                Err(FieldError::NullInvalidForNonNullType(
                                    field_name.to_string(),
                                ))
                            } else {
                                Ok(())
                            }
                        }
                    },
                    Type::Number => match value {
                        Value::Bool(_) => Err(FieldError::BooleanInvalidForNumberType(
                            field_name.to_string(),
                        )),
                        Value::Number(_) => Ok(()),
                        Value::String(_) => Err(FieldError::StringInvalidForNumberType(
                            field_name.to_string(),
                        )),
                        Value::Array(_) => Err(FieldError::ArrayInvalidForNumberType(
                            field_name.to_string(),
                        )),
                        Value::Object(_) => Err(FieldError::ObjectInvalidForNumberType(
                            field_name.to_string(),
                        )),
                        Value::Null => {
                            if !type_declaration.nullable {
                                Err(FieldError::NullInvalidForNonNullType(
                                    field_name.to_string(),
                                ))
                            } else {
                                Ok(())
                            }
                        }
                    },
                    Type::String => match value {
                        Value::Bool(_) => Err(FieldError::BooleanInvalidForStringType(
                            field_name.to_string(),
                        )),
                        Value::Number(_) => Err(FieldError::NumberInvalidForStringType(
                            field_name.to_string(),
                        )),
                        Value::String(_) => Ok(()),
                        Value::Array(_) => Err(FieldError::ArrayInvalidForStringType(
                            field_name.to_string(),
                        )),
                        Value::Object(_) => Err(FieldError::ObjectInvalidForStringType(
                            field_name.to_string(),
                        )),
                        Value::Null => {
                            if !type_declaration.nullable {
                                Err(FieldError::NullInvalidForNonNullType(
                                    field_name.to_string(),
                                ))
                            } else {
                                Ok(())
                            }
                        }
                    },
                    Type::Array { nested_type } => match value {
                        Value::Bool(_) => Err(FieldError::BooleanInvalidForArrayType(
                            field_name.to_string(),
                        )),
                        Value::Number(_) => Err(FieldError::NumberInvalidForArrayType(
                            field_name.to_string(),
                        )),
                        Value::String(_) => Err(FieldError::StringInvalidForArrayType(
                            field_name.to_string(),
                        )),
                        Value::Array(_) => {
                            let array = value.as_array().unwrap();
                            for (i, ele) in array.iter().enumerate() {
                                self.validate_type(
                                    &format!("{}[{}]", field_name, i),
                                    nested_type,
                                    ele,
                                )?;
                            }
                            Ok(())
                        }
                        Value::Object(_) => Err(FieldError::ObjectInvalidForArrayType(
                            field_name.to_string(),
                        )),
                        Value::Null => {
                            if !type_declaration.nullable {
                                Err(FieldError::NullInvalidForNonNullType(
                                    field_name.to_string(),
                                ))
                            } else {
                                Ok(())
                            }
                        }
                    },
                    Type::Object { nested_type } => match value {
                        Value::Bool(_) => Err(FieldError::BooleanInvalidForObjectType(
                            field_name.to_string(),
                        )),
                        Value::Number(_) => Err(FieldError::NumberInvalidForObjectType(
                            field_name.to_string(),
                        )),
                        Value::String(_) => Err(FieldError::StringInvalidForObjectType(
                            field_name.to_string(),
                        )),
                        Value::Array(_) => Err(FieldError::ArrayInvalidForObjectType(
                            field_name.to_string(),
                        )),
                        Value::Object(_) => {
                            let object = value.as_object().unwrap();
                            for (object_key, object_value) in object.iter() {
                                self.validate_type(
                                    &format!("{}{{{}}}", field_name, object_key),
                                    nested_type,
                                    object_value,
                                )?;
                            }
                            Ok(())
                        }
                        Value::Null => {
                            if !type_declaration.nullable {
                                Err(FieldError::NullInvalidForNonNullType(
                                    field_name.to_string(),
                                ))
                            } else {
                                Ok(())
                            }
                        }
                    },
                    Type::Struct { fields } => match value {
                        Value::Bool(_) => Err(FieldError::BooleanInvalidForStructType(
                            field_name.to_string(),
                        )),
                        Value::Number(_) => Err(FieldError::NumberInvalidForStructType(
                            field_name.to_string(),
                        )),
                        Value::String(_) => Err(FieldError::StringInvalidForStructType(
                            field_name.to_string(),
                        )),
                        Value::Array(_) => Err(FieldError::ArrayInvalidForStructType(
                            field_name.to_string(),
                        )),
                        Value::Object(_) => {
                            let object = value.as_object().unwrap();
                            self.validate_struct(field_name, fields, object)?;
                            Ok(())
                        }
                        Value::Null => {
                            if !type_declaration.nullable {
                                Err(FieldError::NullInvalidForNonNullType(
                                    field_name.to_string(),
                                ))
                            } else {
                                Ok(())
                            }
                        }
                    },
                    Type::Union { cases } => match value {
                        Value::Bool(_) => Err(FieldError::BooleanInvalidForUnionType(
                            field_name.to_string(),
                        )),
                        Value::Number(_) => Err(FieldError::NumberInvalidForUnionType(
                            field_name.to_string(),
                        )),
                        Value::String(_) => Err(FieldError::StringInvalidForUnionType(
                            field_name.to_string(),
                        )),
                        Value::Array(_) => {
                            Err(FieldError::ArrayInvalidForUnionType(field_name.to_string()))
                        }
                        Value::Object(_) => {
                            let object = value.as_object().unwrap();
                            self.validate_union(field_name, cases, object)?;
                            Ok(())
                        }
                        Value::Null => {
                            if !type_declaration.nullable {
                                Err(FieldError::NullInvalidForNonNullType(
                                    field_name.to_string(),
                                ))
                            } else {
                                Ok(())
                            }
                        }
                    },
                    Type::Enum { allowed_values } => match value {
                        Value::Bool(_) => Err(FieldError::BooleanInvalidForEnumType(
                            field_name.to_string(),
                        )),
                        Value::Number(_) => {
                            Err(FieldError::NumberInvalidForEnumType(field_name.to_string()))
                        }
                        Value::String(_) => {
                            let enum_value = value.as_str().unwrap().to_string();
                            if !allowed_values.contains(&enum_value) {
                                Err(FieldError::InvalidEnumValue(field_name.to_string()))
                            } else {
                                Ok(())
                            }
                        }
                        Value::Array(_) => {
                            Err(FieldError::ArrayInvalidForEnumType(field_name.to_string()))
                        }
                        Value::Object(_) => {
                            Err(FieldError::ObjectInvalidForEnumType(field_name.to_string()))
                        }
                        Value::Null => {
                            if !type_declaration.nullable {
                                Err(FieldError::NullInvalidForNonNullType(
                                    field_name.to_string(),
                                ))
                            } else {
                                Ok(())
                            }
                        }
                    },
                    Type::Any => match value {
                        Value::Null => {
                            if !type_declaration.nullable {
                                Err(FieldError::NullInvalidForNonNullType(
                                    field_name.to_string(),
                                ))
                            } else {
                                Ok(())
                            }
                        }
                        _ => Ok(()),
                    },
                    Type::Null => match value {
                        Value::Null => Ok(()),
                        _ => Err(FieldError::NonNullInvalidForNullType(
                            field_name.to_string(),
                        )),
                    },
                }
            }
        }
    }
}
