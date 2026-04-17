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
