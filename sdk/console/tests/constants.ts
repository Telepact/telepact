//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

export const schema = `[
  {
    "info.DevConsole": {}
  },
  {
    "fn.fn1": {
      "input1": ["string"],
      "input2": ["integer"]
    },
    "->": [
      {
        "Ok_": {
          "output1": ["array", ["struct.Struct1"]]
        }
      }
    ]
  },
  {
    "struct.Pad1": {
      "field1": ["string"],
      "field2": ["integer"]
    }
  },
  {
    "struct.Pad2": {
      "field1": ["string"],
      "field2": ["integer"]
    }
  },
  {
    "struct.Pad3": {
      "field1": ["string"],
      "field2": ["integer"]
    }
  },
  {
    "struct.Struct1": {
      "field1": ["string"],
      "field2": ["integer"]
    }
  }
]`;