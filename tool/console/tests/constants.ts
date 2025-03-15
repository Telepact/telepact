export const demoSchema = `[
  {
    "///": " A calculator app that provides basic math computation capabilities. ",
    "info.Calculator": {}
  },
  {
    "///": " Compute the \`result\` of the given \`x\` and \`y\` values. ",
    "fn.compute": {
      "x": ["union.Value"],
      "y": ["union.Value"],
      "op": ["union.Operation"]
    },
    "->": [
      {
        "Ok_": {
          "result": ["number"]
        }
      },
      {
        "ErrorCannotDivideByZero": {}
      }
    ]
  },
  {
    "///": " Export all saved variables, up to an optional \`limit\`. ",
    "fn.exportVariables": {
      "limit!": ["integer"]
    },
    "->": [
      {
        "Ok_": {
          "variables": ["array", ["struct.Variable"]]
        }
      }
    ]
  },
  {
    "///": " A function template. ",
    "fn.getPaperTape": {},
    "->": [
      {
        "Ok_": {
          "tape": ["array", ["struct.Computation"]]
        }
      }
    ]
  },
  {
    "///": " Save a set of variables as a dynamic map of variable names to their value. ",
    "fn.saveVariables": {
      "variables": ["object", ["number"]]
    },
    "->": [
      {
        "Ok_": {}
      }
    ]
  },
  {
    "fn.showExample": {},
    "->": [
      {
        "Ok_": {
          "link": ["fn.compute"]
        }
      }
    ]
  },
  {
    "///": " A computation. ",
    "struct.Computation": {
      "firstOperand": ["union.Value"],
      "secondOperand": ["union.Value"],
      "operation": ["union.Operation"],
      "timestamp": ["integer"],
      "successful": ["boolean"]
    }
  },
  {
    "///": " A mathematical variable represented by a \`name\` that holds a certain \`value\`. ",
    "struct.Variable": {
      "name": ["string"],
      "value": ["number"]
    }
  },
  {
    "///": " A basic mathematical operation. ",
    "union.Operation": [
      {
        "Add": {}
      },
      {
        "Sub": {}
      },
      {
        "Mul": {}
      },
      {
        "Div": {}
      }
    ]
  },
  {
    "///": " A value for computation that can take either a constant or variable form. ",
    "union.Value": [
      {
        "Constant": {
          "value": ["number"]
        }
      },
      {
        "Variable": {
          "name": ["string"]
        }
      }
    ]
  }
]`;