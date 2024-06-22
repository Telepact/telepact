import { Message } from '../Message';
import { UTypeDeclaration } from '../internal/types/UTypeDeclaration';
import { UUnion } from '../internal/types/UUnion';
import { ValidationFailure } from '../internal/validation/ValidationFailure';
import { UType } from '../internal/types/UType';
import { UApiSchema } from '../UApiSchema';
import { selectStructFields } from '../internal/SelectStructFields';
import { getInvalidErrorMessage } from '../internal/validation/GetInvalidErrorMessage';
import { validateHeaders } from '../internal/validation/ValidateHeaders';
import { validateResult } from '../internal/validation/ValidateResult';
import { UFn } from '../internal/types/UFn';

export async function handleMessage(
    requestMessage: Message,
    uApiSchema: UApiSchema,
    handler: (message: Message) => Promise<Message>,
    onError: (error: Error) => void,
): Promise<Message> {
    const responseHeaders: Record<string, any> = {};
    const requestHeaders: Record<string, any> = requestMessage.header;
    const requestBody: Record<string, any> = requestMessage.body;
    const parsedUApiSchema: Record<string, UType> = uApiSchema.parsed;
    const requestEntry: [string, any] = Object.entries(requestBody)[0];

    const requestTargetInit = requestEntry[0];
    const requestPayload = requestEntry[1] as Record<string, any>;

    let unknownTarget: string | null;
    let requestTarget: string;
    if (!(requestTargetInit in parsedUApiSchema)) {
        unknownTarget = requestTargetInit;
        requestTarget = 'fn.ping_';
    } else {
        unknownTarget = null;
        requestTarget = requestTargetInit;
    }

    const functionType = parsedUApiSchema[requestTarget] as UFn;
    const resultUnionType: UUnion = functionType.result;

    const callId = requestHeaders['id_'];
    if (callId !== undefined) {
        responseHeaders['id_'] = callId;
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
        uApiSchema.parsedRequestHeaders,
        functionType,
    );
    if (requestHeaderValidationFailures.length > 0) {
        return getInvalidErrorMessage(
            'ErrorInvalidRequestHeaders_',
            requestHeaderValidationFailures,
            resultUnionType,
            responseHeaders,
        );
    }

    if ('bin_' in requestHeaders) {
        const clientKnownBinaryChecksums = requestHeaders['bin_'] as any[];

        responseHeaders['_binary'] = true;
        responseHeaders['_clientKnownBinaryChecksums'] = clientKnownBinaryChecksums;

        if ('_pac' in requestHeaders) {
            responseHeaders['_pac'] = requestHeaders['_pac'];
        }
    }

    const selectStructFieldsHeader: Record<string, any> | null = requestHeaders['select_'] || null;

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

    const functionTypeCall: UUnion = functionType.call;

    const callValidationFailures: ValidationFailure[] = functionTypeCall.validate(requestBody, null, null, [], []);
    if (callValidationFailures.length > 0) {
        return getInvalidErrorMessage(
            'ErrorInvalidRequestBody_',
            callValidationFailures,
            resultUnionType,
            responseHeaders,
        );
    }

    const unsafeResponseEnabled = requestHeaders['unsafe_'] || false;

    const callMessage: Message = new Message(requestHeaders, { [requestTarget]: requestPayload });

    let resultMessage: Message;
    if (requestTarget === 'fn.ping_') {
        resultMessage = new Message({}, { Ok_: {} });
    } else if (requestTarget === 'fn.api_') {
        resultMessage = new Message({}, { Ok_: { api: uApiSchema.original } });
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

    resultMessage.header = { ...resultMessage.header, ...responseHeaders };
    const finalResponseHeaders: Record<string, any> = resultMessage.header;

    const skipResultValidation: boolean = unsafeResponseEnabled;
    if (!skipResultValidation) {
        const resultValidationFailures: ValidationFailure[] = resultUnionType.validate(
            resultUnion,
            selectStructFieldsHeader,
            null,
            [],
            [],
        );
        if (resultValidationFailures.length > 0) {
            return getInvalidErrorMessage(
                'ErrorInvalidResponseBody_',
                resultValidationFailures,
                resultUnionType,
                responseHeaders,
            );
        }
        const responseHeaderValidationFailures: ValidationFailure[] = validateHeaders(
            finalResponseHeaders,
            uApiSchema.parsedResponseHeaders,
            functionType,
        );
        if (responseHeaderValidationFailures.length > 0) {
            return getInvalidErrorMessage(
                'ErrorInvalidResponseHeaders_',
                responseHeaderValidationFailures,
                resultUnionType,
                responseHeaders,
            );
        }
    }

    let finalResultUnion: Record<string, any>;
    if (selectStructFieldsHeader !== null) {
        finalResultUnion = selectStructFields(
            new UTypeDeclaration(resultUnionType, false, []),
            resultUnion,
            selectStructFieldsHeader,
        ) as Record<string, any>;
    } else {
        finalResultUnion = resultUnion;
    }

    return new Message(finalResponseHeaders, finalResultUnion);
}
