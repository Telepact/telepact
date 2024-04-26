import * as prettier from 'prettier';
import pkg from 'prettier/parser-babel';
const { parsers: babelParsers } = pkg;

function padLength(strings) {
    const paddedStrings = strings.map(str => {
        const paddingLength = Math.max(0, 80 - str.length);
        return ' ' + str.padEnd(str.length + paddingLength);
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
    } else if (typeof obj === 'object' && obj !== null) {
        let newObj = {};
        for (const [k, v] of Object.entries(obj)) {
            if (k === '///') {
                let docstring;
                if (typeof v === 'string') {
                    docstring = v;
                } else {
                    docstring = v.map(e => e.trim()).join('\n');
                }

                const formattedWhole = await prettier.format(docstring, {parser: 'markdown', printWidth: 78, proseWrap: "always"})

                const formatted = formattedWhole.split('\n');

                formatted.pop();

                if (formatted.length === 1) {
                    newObj[k] = ' ' + formatted[0] + ' ';
                } else {
                    newObj[k] = padLength(formatted);
                }
            } else {
                newObj[k] = await formatDocstrings(v)
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

const jsonParser = babelParsers['json-stringify'];

const { parse } = jsonParser;

const jsonExtendedParser = {
  ...jsonParser,
  parse: async (text, parsers, options) => {
    console.log('Before parsing...');
    const preprocessedText = await preprocess(text);
    const ast = parse(preprocessedText, parsers, options);
    console.log('After parsing...');
    return ast;
  },
};

const jsonExtended = {
  name: 'uapi',
  parsers: ['uapi-parse'],
  extensions: ['.uapi.json'],
};

export default {
  languages: [jsonExtended],
  parsers: {
    'uapi-parse': jsonExtendedParser,
  },
};