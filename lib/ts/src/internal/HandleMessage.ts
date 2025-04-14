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

import { Message } from '../Message';
import { TTypeDeclaration } from './types/TTypeDeclaration';
import { TUnion } from './types/TUnion';
import { ValidationFailure } from '../internal/validation/ValidationFailure';
import { TType } from './types/TType';
import { TelepactSchema } from '../TelepactSchema';
import { selectStructFields } from '../internal/SelectStructFields';
import { getInvalidErrorMessage } from '../internal/validation/GetInvalidErrorMessage';
import { validateHeaders } from '../internal/validation/ValidateHeaders';
import { validateResult } from '../internal/validation/ValidateResult';
import { mapValidationFailuresToInvalidFieldCases } from './validation/MapValidationFailuresToInvalidFieldCases';
import { ValidateContext } from './validation/ValidateContext';
import { serverBase64Decode } from './binary/ServerBase64Decode';

export async function handleMessage(
    requestMessage: Message,
    telepactSchema: TelepactSchema,
    handler: (message: Message) => Promise<Message>,
    onError: (error: Error) => void,
): Promise<Message> {
    const responseHeaders: Record<string, any> = {};
    const requestHeaders: Record<string, any> = requestMessage.headers;
    const requestBody: Record<string, any> = requestMessage.body;
    const parsedTelepactSchema: Record<string, TType> = telepactSchema.parsed;
    const requestEntry: [string, any] = Object.entries(requestBody)[0];

    const requestTargetInit = requestEntry[0];
    const requestPayload = requestEntry[1] as Record<string, any>;

    let unknownTarget: string | null;
    let requestTarget: string;
    if (!(requestTargetInit in parsedTelepactSchema)) {
        unknownTarget = requestTargetInit;
        requestTarget = 'fn.ping_';
    } else {
        unknownTarget = null;
        requestTarget = requestTargetInit;
    }

    const functionName = requestTarget;
    const callType = parsedTelepactSchema[requestTarget] as TUnion;
    const resultUnionType: TUnion = parsedTelepactSchema[`${requestTarget}.->`] as TUnion;

    const callId = requestHeaders['@id_'];
    if (callId !== undefined) {
        responseHeaders['@id_'] = callId;
    }

    if ('_parseFailures' in requestHeaders) {
        const parseFailures = requestHeaders['_parseFailures'] as any[];
        const newErrorResult: Record<string, any> = {
            ErrorParseFailure_: { reasons: parseFailures },
        };

        validateResult(resultUnionType, newErrorResult);

        return new Message(responseHeaders, newErrorResult);
    }

    const requestHeaderValidationFailures: ValidationFailure[] = validateHeaders(
        requestHeaders,
        telepactSchema.parsedRequestHeaders,
        functionName,
    );
    if (requestHeaderValidationFailures.length > 0) {
        return getInvalidErrorMessage(
            'ErrorInvalidRequestHeaders_',
            requestHeaderValidationFailures,
            resultUnionType,
            responseHeaders,
        );
    }

    if ('@bin_' in requestHeaders) {
        const clientKnownBinaryChecksums = requestHeaders['@bin_'] as any[];

        responseHeaders['@binary_'] = true;
        responseHeaders['@clientKnownBinaryChecksums_'] = clientKnownBinaryChecksums;

        if ('@pac_' in requestHeaders) {
            responseHeaders['@pac_'] = requestHeaders['@pac_'];
        }
    }

    const selectStructFieldsHeader: Record<string, any> | null = requestHeaders['@select_'] || null;

    if (unknownTarget !== null) {
        const newErrorResult: Record<string, any> = {
            ErrorInvalidRequestBody_: {
                cases: [
                    {
                        path: [unknownTarget],
                        reason: { FunctionUnknown: {} },
                    },
                ],
            },
        };

        validateResult(resultUnionType, newErrorResult);
        return new Message(responseHeaders, newErrorResult);
    }

    const functionTypeCall: TUnion = callType;

    const warnings: ValidationFailure[] = [];
    const filterOutWarnings = (e: ValidationFailure) => {
        const r = e.reason == 'NumberTruncated';
        if (r) {
            warnings.push(e);
        }
        return !r;
    };

    const callValidateCtx = new ValidateContext(null, functionName, false)

    const callValidationFailures: ValidationFailure[] = functionTypeCall
        .validate(requestBody, [], callValidateCtx)
        .filter(filterOutWarnings);
    if (callValidationFailures.length > 0) {
        if (warnings.length > 0) {
            const existingWarnings = responseHeaders['@warn_'] || [];
            const moreWarnings = mapValidationFailuresToInvalidFieldCases(warnings);
            responseHeaders['@warn_'] = existingWarnings.concat(moreWarnings);
        }

        return getInvalidErrorMessage(
            'ErrorInvalidRequestBody_',
            callValidationFailures,
            resultUnionType,
            responseHeaders,
        );
    }

    if (Object.keys(callValidateCtx.bytesCoercions).length > 0) {
        serverBase64Decode(requestBody, callValidateCtx.bytesCoercions);
    }

    const unsafeResponseEnabled = requestHeaders['@unsafe_'] || false;

    const callMessage: Message = new Message(requestHeaders, { [functionName]: requestPayload });

    let resultMessage: Message;
    if (functionName === 'fn.ping_') {
        resultMessage = new Message({}, { Ok_: {} });
    } else if (functionName === 'fn.api_') {
        resultMessage = new Message({}, { Ok_: { api: telepactSchema.original } });
    } else {
        try {
            resultMessage = await handler(callMessage);
        } catch (e) {
            try {
                onError(e);
            } catch (error) {
                // Ignore error
            }
            return new Message(responseHeaders, { ErrorUnknown_: {} });
        }
    }

    const resultUnion: Record<string, any> = resultMessage.body;

    resultMessage.headers = { ...resultMessage.headers, ...responseHeaders };
    const finalResponseHeaders: Record<string, any> = resultMessage.headers;

    const skipResultValidation: boolean = unsafeResponseEnabled;

    const coerceBase64 = requestHeaders["@binary_"] != true
    const resultValidateCtx = new ValidateContext(selectStructFieldsHeader, functionName, coerceBase64);
    const resultValidationFailures: ValidationFailure[] = resultUnionType
        .validate(resultUnion, [], resultValidateCtx)
        .filter(filterOutWarnings);

    if (warnings.length > 0) {
        const existingWarnings = responseHeaders['@warn_'] || [];
        const moreWarnings = mapValidationFailuresToInvalidFieldCases(warnings);
        responseHeaders['@warn_'] = existingWarnings.concat(moreWarnings);
    }

    if (resultValidationFailures.length > 0 && !skipResultValidation) {
        return getInvalidErrorMessage(
            'ErrorInvalidResponseBody_',
            resultValidationFailures,
            resultUnionType,
            responseHeaders,
        );
    }

    if (Object.keys(resultValidateCtx.base64Coercions).length > 0) {
        finalResponseHeaders['@base64_'] = resultValidateCtx.base64Coercions;
    }

    if (Object.keys(resultValidateCtx.bytesCoercions).length > 0) {
        serverBase64Decode(resultUnion, resultValidateCtx.bytesCoercions);
    }

    const responseHeaderValidationFailures: ValidationFailure[] = validateHeaders(
        finalResponseHeaders,
        telepactSchema.parsedResponseHeaders,
        functionName
    );
    if (responseHeaderValidationFailures.length > 0) {
        return getInvalidErrorMessage(
            'ErrorInvalidResponseHeaders_',
            responseHeaderValidationFailures,
            resultUnionType,
            responseHeaders,
        );
    }

    let finalResultUnion: Record<string, any>;
    if (selectStructFieldsHeader !== null) {
        finalResultUnion = selectStructFields(
            new TTypeDeclaration(resultUnionType, false, []),
            resultUnion,
            selectStructFieldsHeader,
        ) as Record<string, any>;
    } else {
        finalResultUnion = resultUnion;
    }

    return new Message(finalResponseHeaders, finalResultUnion);
}
