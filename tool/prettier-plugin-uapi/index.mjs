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

const { concat, indent, line, softline, hardline, join } = prettier.doc.builders;

function printJsonAst(path, options, print) {
    const node = path.getValue();

    if (node.type === "JsonRoot") {
        return path.call(print, "node");
    }

    if (node.type === "ArrayExpression") {
        const parent = path.getParentNode();
        const isRoot = parent.type === "JsonRoot";
        const isComment = parent && parent.type === "ObjectProperty" && parent.key.value === "///";

        if (isRoot || isComment) {
            return [
                "[",
                indent(concat([softline, join(concat([",", softline]), path.map(print, "elements"))])),
                softline,
                "]",
            ];
        } else {
            return concat(["[", join(", ", path.map(print, "elements")), "]"]);
        }
    }

    if (node.type === "ObjectExpression") {
        return node.properties.length === 0
            ? "{}"
            : [
                  "{",
                  indent(concat([softline, join(concat([",", line]), path.map(print, "properties"))])),
                  softline,
                  "}",
              ];
    }

    if (node.type === "StringLiteral") {
        return `"${node.value}"`;
    }

    if (node.type === "NumericLiteral") {
        return node.value.toString();
    }

    if (node.type === "BooleanLiteral") {
        return node.value ? "true" : "false";
    }

    if (node.type === "NullLiteral") {
        return "null";
    }

    if (node.type === "ObjectProperty") {
        return concat([path.call(print, "key"), ": ", path.call(print, "value")]);
    }

    console.log(`Node type not handled: ${node.type}`);

    return "";
}

const jsonParser = babelParsers["json-stringify"];
const jsonPrinter = jsonParser.printer;

const jsonExtendedPrinter = {
    ...jsonPrinter,
    print: printJsonAst,
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
