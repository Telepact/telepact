import syncPrettier  from '@prettier/sync';
import * as prettierPluginBabel from 'prettier/plugins/babel';

function padLength(strings) {
    const paddedStrings = strings.map(str => {
        const paddingLength = Math.max(0, 80 - str.length);
        return ' ' + str.padEnd(str.length + paddingLength);
    });
    return paddedStrings;
}

function formatDocstrings(obj) {
    if (Array.isArray(obj)) {
        for (const e of obj) {
            formatDocstrings(e);
        }
    } else if (typeof obj === 'object' && obj !== null) {
        for (const [k, v] of Object.entries(obj)) {
            if (k === '///') {
                let docstring;
                if (typeof v === 'string') {
                    docstring = v;
                } else {
                    docstring = v.map(e => e.trim()).join('\n');
                }

                const formattedWhole = syncPrettier.format(docstring, {parser: 'markdown', printWidth: 78, proseWrap: "always"})

                const formatted = formattedWhole.split('\n');

                formatted.pop();

                if (formatted.length === 1) {
                    obj[k] = ' ' + formatted[0] + ' ';
                } else {
                    obj[k] = padLength(formatted);
                }
            } else {
                formatDocstrings(v)
            }
        }
    }
}

function preprocess(text) {
    let json = JSON.parse(text);

    formatDocstrings(json);

    return JSON.stringify(json, null, 4);
}

export const parsers = {
    json: {
        ...prettierPluginBabel.parsers.json,
        preprocess
    }
}