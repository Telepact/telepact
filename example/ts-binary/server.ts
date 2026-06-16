//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import * as fs from 'node:fs';
import * as path from 'node:path';
import { FunctionRouter, Message, Server, ServerOptions, TelepactSchema, TelepactSchemaFiles } from 'telepact';

async function getNumbers(functionName: string, requestMessage: Message): Promise<Message> {
    const argument = requestMessage.body[functionName] as Record<string, number>;
    const limit = argument['limit'];
    return new Message({}, {
        'Ok_': {
            'values': Array.from({ length: limit }, (_value, index) => index + 1),
        },
    });
}

export function buildTelepactServer(): Server {
    const files = new TelepactSchemaFiles('api', fs, path);
    const schema = TelepactSchema.fromFileJsonMap(files.filenamesToJson);
    const options = new ServerOptions();
    options.authRequired = false;
    const functionRouter = new FunctionRouter({ 'fn.getNumbers': getNumbers });
    return new Server(schema, functionRouter, options);
}
