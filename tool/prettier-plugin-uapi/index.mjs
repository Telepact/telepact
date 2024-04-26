import * as prettier from "prettier";
import parserPkg from "prettier/parser-babel";
const { parsers: babelParsers } = parserPkg;

function padLength(strings) {
    const paddedStrings = strings.map((str) => {
        const paddingLength = Math.max(0, 80 - str.length);
        return " " + str.padEnd(str.length + paddingLength);
    });
    return paddedStrings;
}

async function formatDocstrings(obj) {
    if (Array.isArray(obj)) {
        let newArr = [];
        for (const e of obj) {
            let formatted = await formatDocstrings(e);
            newArr.push(formatted);
        }
        return newArr;
    } else if (typeof obj === "object" && obj !== null) {
        let newObj = {};
        for (const [k, v] of Object.entries(obj)) {
            if (k === "///") {
                let docstring;
                if (typeof v === "string") {
                    docstring = v;
                } else {
                    docstring = v.map((e) => e.trim()).join("\n");
                }

                const formattedWhole = await prettier.format(docstring, {
                    parser: "markdown",
                    printWidth: 78,
                    proseWrap: "always",
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

async function preprocess(text) {
    let json = JSON.parse(text);

    const newJson = await formatDocstrings(json);

    const result = JSON.stringify(newJson, null, 4);

    return result;
}

const jsonParser = babelParsers["json-stringify"];
const jsonPrinter = jsonParser.printer;

const jsonExtendedPrinter = {
    ...jsonPrinter,
    print(path, options, print) {
        const node = path.getValue();

        if (node.type === "JsonRoot") {
            return path.call(print, "node");
        }

        let tabWidth = options.tabWidth;
        console.log(`Node type: ${node.type}`);
        console.log(`Tab width: ${tabWidth}`);

        const depth = (path.stack.length - 1) / 2 - 1;
        console.log(`depth: ${depth}`);
        const indentation = " ".repeat(tabWidth * depth);
        const indentationR = depth > 0 ? " ".repeat(tabWidth * (depth - 1)) : "";

        if (node.type === "ArrayExpression") {
            if (
                path.getParentNode().type === "JsonRoot" ||
                (path.getParentNode().type === "ObjectProperty" && path.getParentNode().key.value === "///")
            ) {
                // This is the root level array, format with newlines
                return [
                    "[",
                    path
                        .map(print, "elements")
                        .map((e) => indentation + e)
                        .join(",\n"),
                    indentationR + "]",
                ].join("\n");
            } else {
                // This is a nested array, format inline
                return ["[", path.map(print, "elements").join(", "), "]"].join("");
            }
        } else if (node.type === "ObjectExpression") {
            // This is an object, format with newlines and indentation
            return [
                "{",
                path
                    .map(print, "properties")
                    .map((e) => indentation + e)
                    .join(",\n"),
                indentationR + "}",
            ].join("\n");
        } else if (node.type === "ObjectProperty") {
            // This is a property, print the key and the value
            const key = path.call(print, "key");
            const value = path.call(print, "value");
            return `${key}: ${value}`;
        } else if (node.type === "StringLiteral") {
            // This is a string, format with double quotes
            return `"${node.value}"`;
        } else if (node.type === "NumericLiteral") {
            // This is a number, format as is
            return node.value;
        } else if (node.type === "BooleanLiteral") {
            // This is a boolean, format as is
            return node.value;
        } else if (node.type === "NullLiteral") {
            // This is null, format as is
            return "null";
        }

        return print(path);
    },
};

const { parse } = jsonParser;

const jsonExtendedParser = {
    ...jsonParser,
    parse: async (text, parsers, options) => {
        console.log("Before parsing...");
        const preprocessedText = await preprocess(text);
        const ast = parse(preprocessedText, parsers, options);
        console.log("After parsing...");
        return ast;
    },
    astFormat: "uapi-ast",
};

const jsonExtended = {
    name: "uapi",
    parsers: ["uapi-parse"],
    extensions: [".uapi.json"],
};

export default {
    languages: [jsonExtended],
    parsers: {
        "uapi-parse": jsonExtendedParser,
    },
    printers: {
        "uapi-ast": jsonExtendedPrinter,
    },
};
