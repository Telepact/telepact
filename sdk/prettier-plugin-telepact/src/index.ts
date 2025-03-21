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
        return node.properties.length === 0
            ? "{}"
            : [
                  "{",
                  indent(group([hardline, join(group([",", hardline]), path.map(print, "properties"))])),
                  hardline,
                  "}",
              ];
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

    console.log(`Node type not handled: ${node.type}`);

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
        console.log("Before parsing...");
        const preprocessedText = await preprocess(text);
        const ast = parse(preprocessedText, options);
        console.log("After parsing...");
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
