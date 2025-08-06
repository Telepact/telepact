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

import { parsers as babelParsers } from "prettier/plugins/babel";
import markdownPlugin from "prettier/plugins/markdown";
import { Plugin, Parser, ParserOptions, SupportLanguage, format as prettierFormat, doc, Printer, getSupportInfo } from "prettier";

function padLength(strings: string[]): string[] {
    const paddedStrings = strings.map((str) => {
        const paddingLength = Math.max(0, 80 - str.length);
        return " " + str.padEnd(str.length + paddingLength);
    });
    return paddedStrings;
}

async function formatDocstrings(obj: any): Promise<any> {
    if (Array.isArray(obj)) {
        let newArr = [];
        for (const e of obj) {
            let formatted = await formatDocstrings(e);
            newArr.push(formatted);
        }
        return newArr;
    } else if (typeof obj === "object" && obj !== null) {
        let newObj: any = {};
        for (const [k, v] of Object.entries(obj)) {
            if (k === "///") {
                let docstring;
                if (typeof v === "string") {
                    docstring = v;
                } else {
                    docstring = (v as Array<string>).map((e: string) => e.trim()).join("\n");
                }

                const formattedWhole = await prettierFormat(docstring, {
                    parser: "markdown",
                    printWidth: 78,
                    proseWrap: "always",
                    plugins: [markdownPlugin],
                });

                const formatted = formattedWhole.split("\n");

                formatted.pop();

                if (formatted.length === 1) {
                    newObj[k] = " " + formatted[0] + " ";
                } else {
                    newObj[k] = padLength(formatted);
                }
            } else {
                newObj[k] = await formatDocstrings(v);
            }
        }
        return newObj;
    } else {
        return obj;
    }
}

async function preprocess(text: string): Promise<string> {
    let json = JSON.parse(text);

    const newJson = await formatDocstrings(json);

    const result = JSON.stringify(newJson, null, 4);

    return result;
}

const { group, line, softline, hardline, join, indent } = doc.builders;

function printJsonAst(path: any, options: any, print: any): any {
    const node = path.getValue();

    if (node.type === "JsonRoot") {
        return path.call(print, "node");
    }

    if (node.type === "ArrayExpression") {
        const parent = path.getParentNode();
        const isRoot = parent.type === "JsonRoot";
        const isComment = parent && parent.type === "ObjectProperty" && parent.key.value === "///";
        const isUnion = parent && parent.type === "ObjectProperty" && (parent.key.value.includes("union.") || parent.key.value.includes("errors.") || parent.key.value === "->");

        if (isRoot || isComment || isUnion) {
            return [
                "[",
                indent(group([hardline, join(group([",", hardline]), path.map(print, "elements"))])),
                hardline,
                "]",
            ];
        } else {
            return group(["[", join(", ", path.map(print, "elements")), "]"]);
        }
    }

    if (node.type === "ObjectExpression") {
        const isDownstreamOfLowercaseKey = () => {
            let currentNode = path.node;
            let parentNode = path.getParentNode();

            while (parentNode) {
                console.log("Checking parent node:", parentNode.type);

                if (
                    parentNode.type === "Property" ||
                    parentNode.type === "ObjectProperty"
                ) {
                    const key = parentNode.key;
                    const keyName = key.type === "Identifier" ? key.name : key.value;

                    if (keyName && typeof keyName === 'string' && (/^@[a-z][a-zA-Z0-9_]*$/.test(keyName) || /^([a-z][a-zA-Z0-9_]*)(!)?$/.test(keyName))) {
                        console.log(`Found a lowercase key ancestor: "${keyName}". Formatting on one line.`);
                        return true;
                    }
                }

                currentNode = parentNode;
                parentNode = path.getParentNode(currentNode);
            }
            console.log("No lowercase key ancestor found. Using multi-line format.");
            return false;
        };

        const properties = path.map(print, "properties");

        if (node.properties.length === 0 || isDownstreamOfLowercaseKey()) {
            return ["{", join(", ", properties), "}"];
        } else {
            return [
                "{",
                indent(group([hardline, join(group([",", hardline]), properties)])),
                hardline,
                "}",
            ];
        }
    }

    if (node.type === "StringLiteral") {
        return JSON.stringify(node.value);
    }

    if (node.type === "NumericLiteral") {
        return JSON.stringify(node.value);
    }

    if (node.type === "BooleanLiteral") {
        return node.value ? "true" : "false";
    }

    if (node.type === "NullLiteral") {
        return "null";
    }

    if (node.type === "ObjectProperty") {
        return group([path.call(print, "key"), ": ", path.call(print, "value")]);
    }

    return "";
}

const jsonParser = babelParsers["json-stringify"];

const jsonExtendedPrinter: Printer = {
    print: printJsonAst,
};

const { parse } = jsonParser;

const jsonExtendedParser: Parser = {
    ...jsonParser,
    parse: async (text: string, options: ParserOptions) => {
        const preprocessedText = await preprocess(text);
        const ast = parse(preprocessedText, options);
        return ast;
    },
    astFormat: "telepact-ast",
};

const jsonExtended: SupportLanguage = {
    name: "telepact",
    parsers: ["telepact-parse"],
    extensions: [".telepact.json"],
};

const plugin: Plugin = {
    languages: [jsonExtended],
    parsers: {
        "telepact-parse": jsonExtendedParser,
    },
    printers: {
        "telepact-ast": jsonExtendedPrinter,
    },
};

export default plugin;
