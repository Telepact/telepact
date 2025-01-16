import { Message } from '../../Message';
import { MockInvocation } from '../../internal/mock/MockInvocation';
import { MockStub } from '../../internal/mock/MockStub';
import { RandomGenerator } from '../../RandomGenerator';
import { UApiSchema } from '../../UApiSchema';
import { isSubMap } from '../../internal/mock/IsSubMap';
import { verify } from '../../internal/mock/Verify';
import { verifyNoMoreInteractions } from '../../internal/mock/VerifyNoMoreInteractions';
import { UApiError } from '../../UApiError';
import { UFn } from '../../internal/types/UFn';
import { objectsAreEqual } from '../../internal/ObjectsAreEqual';
import { GenerateContext } from '../generation/GenerateContext';

export async function mockHandle(
    requestMessage: Message,
    stubs: MockStub[],
    invocations: MockInvocation[],
    random: RandomGenerator,
    uApiSchema: UApiSchema,
    enableGeneratedDefaultStub: boolean,
    enableOptionalFieldGeneration: boolean,
    randomizeOptionalFieldGeneration: boolean,
): Promise<Message> {
    const header: Record<string, any> = requestMessage.header;

    const enableGenerationStub = header._gen || false;
    const functionName = requestMessage.getBodyTarget();
    const argument = requestMessage.getBodyPayload();

    if (functionName === 'fn.createStub_') {
        const givenStub = argument.stub as Record<string, any>;

        const stubCall = Object.entries(givenStub).find(([key]) => key.startsWith('fn.'));
        const [stubFunctionName, stubArg] = stubCall as [string, Record<string, any>];
        const stubResult = givenStub['->'] as Record<string, any>;
        const allowArgumentPartialMatch = !argument['strictMatch!'] || false;
        const stubCount = argument['count!'] || -1;

        const stub = new MockStub(stubFunctionName, stubArg, stubResult, allowArgumentPartialMatch, stubCount);

        stubs.unshift(stub);
        return new Message({}, { Ok_: {} });
    } else if (functionName === 'fn.verify_') {
        const givenCall = argument.call as Record<string, any>;

        const call = Object.entries(givenCall).find(([key]) => key.startsWith('fn.'));
        const [callFunctionName, callArg] = call as [string, Record<string, any>];
        const verifyTimes = argument['count!'] || { AtLeast: { times: 1 } };
        const strictMatch = argument['strictMatch!'] || false;

        const verificationResult = verify(callFunctionName, callArg, strictMatch, verifyTimes, invocations);
        return new Message({}, verificationResult);
    } else if (functionName === 'fn.verifyNoMoreInteractions_') {
        const verificationResult = verifyNoMoreInteractions(invocations);
        return new Message({}, verificationResult);
    } else if (functionName === 'fn.clearCalls_') {
        invocations.length = 0;
        return new Message({}, { Ok_: {} });
    } else if (functionName === 'fn.clearStubs_') {
        stubs.length = 0;
        return new Message({}, { Ok_: {} });
    } else if (functionName === 'fn.setRandomSeed_') {
        const givenSeed = argument.seed as number;

        random.setSeed(givenSeed);
        return new Message({}, { Ok_: {} });
    } else {
        invocations.push(new MockInvocation(functionName, argument));

        const definition = uApiSchema.parsed[functionName] as UFn;

        for (const stub of stubs) {
            if (stub.count === 0) {
                continue;
            }
            if (stub.whenFunction === functionName) {
                if (stub.allowArgumentPartialMatch) {
                    if (isSubMap(stub.whenArgument, argument)) {
                        const useBlueprintValue = true;
                        const includeOptionalFields = false;
                        const alwaysIncludeRequiredFields = true;
                        const resultInit = definition.result.generateRandomValue(
                            new GenerateContext(
                                stub.thenResult,
                                useBlueprintValue,
                                includeOptionalFields,
                                randomizeOptionalFieldGeneration,
                                alwaysIncludeRequiredFields,
                                [],
                                random,
                            ),
                        );
                        const result = resultInit as Record<string, any>;
                        if (stub.count > 0) {
                            stub.count -= 1;
                        }
                        return new Message({}, result);
                    }
                } else {
                    if (objectsAreEqual(stub.whenArgument, argument)) {
                        const useBlueprintValue = true;
                        const includeOptionalFields = false;
                        const alwaysIncludeRequiredFields = true;
                        const resultInit = definition.result.generateRandomValue(
                            new GenerateContext(
                                stub.thenResult,
                                useBlueprintValue,
                                includeOptionalFields,
                                randomizeOptionalFieldGeneration,
                                alwaysIncludeRequiredFields,
                                [],
                                random,
                            ),
                        );
                        const result = resultInit as Record<string, any>;
                        if (stub.count > 0) {
                            stub.count -= 1;
                        }
                        return new Message({}, result);
                    }
                }
            }
        }

        if (!enableGeneratedDefaultStub && !enableGenerationStub) {
            return new Message({}, { ErrorNoMatchingStub_: {} });
        }

        if (definition) {
            const resultUnion = definition.result;
            const okStructRef = resultUnion.cases['Ok_'];
            const useBlueprintValue = true;
            const includeOptionalFields = true;
            const alwaysIncludeRequiredFields = true;
            const randomOkStructInit = okStructRef.generateRandomValue(
                new GenerateContext(
                    {},
                    useBlueprintValue,
                    includeOptionalFields,
                    randomizeOptionalFieldGeneration,
                    alwaysIncludeRequiredFields,
                    [],
                    random,
                ),
            );
            const randomOkStruct = randomOkStructInit as Record<string, any>;
            return new Message({}, { Ok_: randomOkStruct });
        } else {
            throw new UApiError(`Unexpected unknown function: ${functionName}`);
        }
    }
}
