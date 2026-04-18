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

import test from "node:test";
import assert from "node:assert/strict";
import prettier from "prettier/standalone";
import markdownPlugin from "prettier/plugins/markdown";
import { parseDocument } from "yaml";

import telepactPlugin from "../dist/index.esm.js";

async function formatTelepactSchema(input) {
    return await prettier.format(input, {
        filepath: "schema.telepact.yaml",
        parser: "telepact-parse",
        printWidth: 78,
        proseWrap: "always",
        plugins: [markdownPlugin, telepactPlugin],
    });
}

test("formats schema JSON into Telepact YAML", async () => {
    const input =
        '[{"///":"Get the telepact `schema` of this server.\\n\\nSet `includeInternal` to `true` to include Telepact internal definitions.","fn.api_":{"includeInternal!":"boolean","includeExamples!":"boolean"},"->":[{"Ok_":{"api":[{"string":"any"}]}}]}]';

    const output = await formatTelepactSchema(input);

    assert.equal(
        output,
        `- ///: |
    Get the telepact \`schema\` of this server.
    
    Set \`includeInternal\` to \`true\` to include Telepact internal definitions.
  fn.api_:
    includeInternal!: "boolean"
    includeExamples!: "boolean"
  ->:
    - Ok_:
        api: [{"string": "any"}]
`,
    );
});

test("preserves the preamble and keeps field-like values inline", async () => {
    const input = `#|
#|  Header
#|

- headers.Auth_:
    "@auth_":
      Session:
        token: string
  ->: {}
`;

    const output = await formatTelepactSchema(input);

    assert.equal(
        output,
        `#|
#|  Header
#|

- headers.Auth_:
    "@auth_": {"Session": {"token": "string"}}
  ->: {}
`,
    );

    assert.equal(parseDocument(output).errors.length, 0);
});

test("formats array docstrings as markdown blocks", async () => {
    const input = `[
  {
    "///": [
      "Calculate the result.",
      "",
      "Returns \`Ok_\` when the expression succeeds."
    ],
    "fn.eval": {
      "expression": "string"
    },
    "->": [
      {
        "Ok_": {
          "result": "number"
        }
      }
    ]
  }
]`;

    const output = await formatTelepactSchema(input);

    assert.equal(
        output,
        `- ///: |
    Calculate the result.
    
    Returns \`Ok_\` when the expression succeeds.
  fn.eval:
    expression: "string"
  ->:
    - Ok_:
        result: "number"
`,
    );

    assert.equal(parseDocument(output).errors.length, 0);
});

test("quotes special keys while keeping Telepact field payloads inline", async () => {
    const input = `- headers.Auth_:
    "@auth_":
      Session:
        token: string
        scopes: []
    x-response-header:
      X-Trace-Id: string
  ->:
    - Ok_:
        headers:
          "@etag": string
`;

    const output = await formatTelepactSchema(input);

    assert.equal(
        output,
        `- headers.Auth_:
    "@auth_": {"Session": {"token": "string", "scopes": []}}
    x-response-header:
      X-Trace-Id: 'string'
  ->:
    - Ok_:
        headers: {"@etag": "string"}
`,
    );

    assert.equal(parseDocument(output).errors.length, 0);
});
