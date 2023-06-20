JSON = '''
{
  "function._ping": [
    [],
    [
      {},
      "-->",
      {}
    ]
  ],
  "function._api": [
    [],
    [
      {},
      "-->",
      {
        "api": "object"
      }
    ]
  ],
  "struct._InvalidField": [
    [],
    {
      "field": "string",
      "reason": "string"
    }
  ],
  "error._InvalidInput": [
    [],
    {
      "cases": "array<struct._InvalidField>"
    }
  ],
  "error._InvalidOutput": [
    [],
    {}
  ],
  "error._ApplicationFailure": [
    [],
    {}
  ]
}
'''


def build(original_api_description: Dict[str, Any]) -> Dict[str, Any]:
    def handler(function_name: str, headers: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "_ping": {},
            "_api": {"api": original_api_description},
        }.get(function_name, FunctionNotFound(function_name))

    return handler
