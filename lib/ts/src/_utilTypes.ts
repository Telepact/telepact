import { _ANY_NAME, _ARRAY_NAME, _BOOLEAN_NAME, _FN_NAME, _INTEGER_NAME, _MOCK_CALL_NAME, _MOCK_STUB_NAME, _OBJECT_NAME, _STRING_NAME, _STRUCT_NAME, _UNION_NAME, clientBinaryDecode, clientBinaryEncode, generateRandomAny, generateRandomArray, generateRandomBoolean, generateRandomFn, generateRandomInteger, generateRandomNumber, generateRandomObject, generateRandomString, generateRandomStruct, generateRandomUnion, generateRandomValueOfType, serverBinaryDecode, serverBinaryEncode, validateArray, validateBoolean, validateInteger, validateMockCall, validateMockStub, validateNumber, validateObject, validateString, validateStruct, validateUnion, validateValueOfType } from "./_util";

export class _SchemaParseFailure {
    constructor(
        public readonly path: any[],
        public readonly reason: string,
        public readonly data: Record<string, any>
    ) {}
}

export class _RandomGenerator {
    private seed: number = 0;
    private collectionLengthMin: number;
    private collectionLengthMax: number;

    constructor(collectionLengthMin: number, collectionLengthMax: number) {
        this.collectionLengthMin = collectionLengthMin;
        this.collectionLengthMax = collectionLengthMax;
    }

    setSeed(seed: number): void {
        this.seed = seed;
    }

    nextInt(): number {
        this.seed = (this.seed * 1_103_515_245 + 12_345) & 0x7fffffff;
        return this.seed;
    }

    nextIntWithCeiling(ceiling: number): number {
        if (ceiling === 0) {
            return 0;
        }
        return this.nextInt() % ceiling;
    }

    nextBoolean(): boolean {
        return this.nextIntWithCeiling(31) > 15;
    }

    nextString(): string {
        const bytes = Buffer.alloc(4);
        bytes.writeInt32LE(this.nextInt(), 0);
        return bytes.toString('base64').replace(/=/g, '');
    }

    nextDouble(): number {
        return (this.nextInt() & 0x7fffffff) / 0x7fffffff;
    }

    nextCollectionLength(): number {
        return this.nextIntWithCeiling(this.collectionLengthMax - this.collectionLengthMin) + this.collectionLengthMin;
    }
}

export interface _UType {
    getTypeParameterCount(): number;
    validate(value: any, typeParameters: _UTypeDeclaration[], generics: _UTypeDeclaration[]): _ValidationFailure[];
    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        includeRandomOptionalFields: boolean,
        typeParameters: _UTypeDeclaration[],
        generics: _UTypeDeclaration[],
        randomGenerator: _RandomGenerator
    ): any;
    getName(generics: _UTypeDeclaration[]): string;
}

export class _UTypeDeclaration {
    constructor(
        public readonly type: _UType,
        public readonly nullable: boolean,
        public readonly typeParameters: _UTypeDeclaration[]
    ) {}

    validate(value: any, generics: _UTypeDeclaration[]): _ValidationFailure[] {
        return validateValueOfType(value, generics, this.type, this.nullable, this.typeParameters);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        includeRandomOptionalFields: boolean,
        generics: _UTypeDeclaration[],
        randomGenerator: _RandomGenerator
    ): any {
        return generateRandomValueOfType(
            blueprintValue,
            useBlueprintValue,
            includeRandomOptionalFields,
            generics,
            randomGenerator,
            this.type,
            this.nullable,
            this.typeParameters
        );
    }
}


export interface _UFieldDeclaration {
    readonly fieldName: string;
    readonly typeDeclaration: _UTypeDeclaration;
    readonly optional: boolean;
}

export class _ValidationFailure {
    constructor(public readonly path: any[],
    public readonly reason: string,
    public readonly data: Record<string, any>) {}
}

export class _UGeneric implements _UType {
    constructor(public readonly index: number) {}

    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: _UTypeDeclaration[], generics: _UTypeDeclaration[]): _ValidationFailure[] {
        const typeDeclaration = generics[this.index]!;
        return typeDeclaration.validate(value, []);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        includeRandomOptionalFields: boolean,
        typeParameters: _UTypeDeclaration[],
        generics: _UTypeDeclaration[],
        randomGenerator: _RandomGenerator
    ): any {
        const genericTypeDeclaration = generics[this.index]!;
        return genericTypeDeclaration.generateRandomValue(
            blueprintValue,
            useBlueprintValue,
            includeRandomOptionalFields,
            [],
            randomGenerator
        );
    }

    getName(generics: _UTypeDeclaration[]): string {
        const typeDeclaration = generics[this.index]!;
        return typeDeclaration.type.getName(generics);
    }
}

export class _UAny implements _UType {
    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: _UTypeDeclaration[], generics: _UTypeDeclaration[]): _ValidationFailure[] {
        return [];
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        includeRandomOptionalFields: boolean,
        typeParameters: _UTypeDeclaration[],
        generics: _UTypeDeclaration[],
        randomGenerator: _RandomGenerator
    ): any {
        return generateRandomAny(randomGenerator);
    }

    getName(generics: _UTypeDeclaration[]): string {
        return _ANY_NAME;
    }
}

export class _UBoolean implements _UType {
    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: _UTypeDeclaration[], generics: _UTypeDeclaration[]): _ValidationFailure[] {
        return validateBoolean(value);
    }

    generateRandomValue(blueprintValue: any, useBlueprintValue: boolean, includeRandomOptionalFields: boolean, typeParameters: _UTypeDeclaration[], generics: _UTypeDeclaration[], randomGenerator: _RandomGenerator): any {
        return generateRandomBoolean(blueprintValue, useBlueprintValue, randomGenerator);
    }

    getName(generics: _UTypeDeclaration[]): string {
        return _BOOLEAN_NAME;
    }
}

export class _UInteger implements _UType {
    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: _UTypeDeclaration[], generics: _UTypeDeclaration[]): _ValidationFailure[] {
        return validateInteger(value);
    }

    generateRandomValue(blueprintValue: any, useBlueprintValue: boolean, includeRandomOptionalFields: boolean, typeParameters: _UTypeDeclaration[], generics: _UTypeDeclaration[], randomGenerator: _RandomGenerator): any {
        return generateRandomInteger(blueprintValue, useBlueprintValue, randomGenerator);
    }

    getName(generics: _UTypeDeclaration[]): string {
        return _INTEGER_NAME;
    }
}

export class _UNumber implements _UType {
    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: _UTypeDeclaration[], generics: _UTypeDeclaration[]): _ValidationFailure[] {
        return validateNumber(value);
    }

    generateRandomValue(blueprintValue: any, useBlueprintValue: boolean, includeRandomOptionalFields: boolean, typeParameters: _UTypeDeclaration[], generics: _UTypeDeclaration[], randomGenerator: _RandomGenerator): any {
        return generateRandomNumber(blueprintValue, useBlueprintValue, randomGenerator);
    }

    getName(generics: _UTypeDeclaration[]): string {
        return "Number";
    }
}

export class _UString implements _UType {
    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: _UTypeDeclaration[], generics: _UTypeDeclaration[]): _ValidationFailure[] {
        return validateString(value);
    }

    generateRandomValue(blueprintValue: any, useBlueprintValue: boolean, includeRandomOptionalFields: boolean, typeParameters: _UTypeDeclaration[], generics: _UTypeDeclaration[], randomGenerator: _RandomGenerator): any {
        return generateRandomString(blueprintValue, useBlueprintValue, randomGenerator);
    }

    getName(generics: _UTypeDeclaration[]): string {
        return _STRING_NAME;
    }
}

export class _UArray implements _UType {
    getTypeParameterCount(): number {
        return 1;
    }

    validate(value: any, typeParameters: _UTypeDeclaration[], generics: _UTypeDeclaration[]): _ValidationFailure[] {
        return validateArray(value, typeParameters, generics);
    }

    generateRandomValue(blueprintValue: any, useBlueprintValue: boolean, includeRandomOptionalFields: boolean, typeParameters: _UTypeDeclaration[], generics: _UTypeDeclaration[], randomGenerator: _RandomGenerator): any {
        return generateRandomArray(blueprintValue, useBlueprintValue, includeRandomOptionalFields, typeParameters, generics, randomGenerator);
    }

    getName(generics: _UTypeDeclaration[]): string {
        return _ARRAY_NAME;
    }
}

export class _UObject implements _UType {
    getTypeParameterCount(): number {
        return 1;
    }

    validate(value: any, typeParameters: _UTypeDeclaration[], generics: _UTypeDeclaration[]): _ValidationFailure[] {
        return validateObject(value, typeParameters, generics);
    }

    generateRandomValue(blueprintValue: any, useBlueprintValue: boolean, includeRandomOptionalFields: boolean, typeParameters: _UTypeDeclaration[], generics: _UTypeDeclaration[], randomGenerator: _RandomGenerator): any {
        return generateRandomObject(blueprintValue, useBlueprintValue, includeRandomOptionalFields, typeParameters, generics, randomGenerator);
    }

    getName(generics: _UTypeDeclaration[]): string {
        return _OBJECT_NAME;
    }
}

export class _UStruct implements _UType {
    constructor(public readonly name: string, public readonly fields: Record<string, _UFieldDeclaration>, public readonly typeParameterCount: number) {}

    getTypeParameterCount(): number {
        return this.typeParameterCount;
    }

    validate(value: any, typeParameters: _UTypeDeclaration[], generics: _UTypeDeclaration[]): _ValidationFailure[] {
        return validateStruct(value, typeParameters, generics, this.fields);
    }

    generateRandomValue(blueprintValue: any, useBlueprintValue: boolean, includeRandomOptionalFields: boolean, typeParameters: _UTypeDeclaration[], generics: _UTypeDeclaration[], random: _RandomGenerator): any {
        return generateRandomStruct(blueprintValue, useBlueprintValue, includeRandomOptionalFields, typeParameters, generics, random, this.fields);
    }

    getName(generics: _UTypeDeclaration[]): string {
        return _STRUCT_NAME;
    }
}

export class _UUnion implements _UType {
    constructor(public readonly name: string, public readonly cases: Record<string, _UStruct>, public readonly typeParameterCount: number) {}

    getTypeParameterCount(): number {
        return this.typeParameterCount;
    }

    validate(value: any, typeParameters: _UTypeDeclaration[], generics: _UTypeDeclaration[]): _ValidationFailure[] {
        return validateUnion(value, typeParameters, generics, this.cases);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        includeRandomOptionalFields: boolean,
        typeParameters: _UTypeDeclaration[],
        generics: _UTypeDeclaration[],
        random: _RandomGenerator
    ): any {
        return generateRandomUnion(
            blueprintValue,
            useBlueprintValue,
            includeRandomOptionalFields,
            typeParameters,
            generics,
            random,
            this.cases
        );
    }

    getName(generics: _UTypeDeclaration[]): string {
        return _UNION_NAME;
    }
}

export class _UFn implements _UType {
    public readonly name: string;
    public readonly call: _UUnion;
    public readonly result: _UUnion;
    public readonly errorsRegex: string;

    constructor(name: string, call: _UUnion, output: _UUnion, errorsRegex: string) {
        this.name = name;
        this.call = call;
        this.result = output;
        this.errorsRegex = errorsRegex;
    }

    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: _UTypeDeclaration[], generics: _UTypeDeclaration[]): _ValidationFailure[] {
        return this.call.validate(value, typeParameters, generics);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        includeRandomOptionalFields: boolean,
        typeParameters: _UTypeDeclaration[],
        generics: _UTypeDeclaration[],
        randomGenerator: _RandomGenerator
    ): any {
        return generateRandomFn(
            blueprintValue,
            useBlueprintValue,
            includeRandomOptionalFields,
            typeParameters,
            generics,
            randomGenerator,
            this.call.cases
        );
    }

    getName(generics: _UTypeDeclaration[]): string {
        return _FN_NAME;
    }
}

export class _UMockCall implements _UType {
    public readonly types: { [key: string]: _UType };

    constructor(types: { [key: string]: _UType }) {
        this.types = types;
    }

    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: _UTypeDeclaration[], generics: _UTypeDeclaration[]): _ValidationFailure[] {
        return validateMockCall(value, typeParameters, generics, this.types);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        includeRandomOptionalFields: boolean,
        typeParameters: _UTypeDeclaration[],
        generics: _UTypeDeclaration[],
        randomGenerator: _RandomGenerator
    ): any {
        throw new Error("Not implemented");
    }

    getName(generics: _UTypeDeclaration[]): string {
        return _MOCK_CALL_NAME;
    }
}

export class _UMockStub implements _UType {
    public readonly types: { [key: string]: _UType };

    constructor(types: { [key: string]: _UType }) {
        this.types = types;
    }

    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: _UTypeDeclaration[], generics: _UTypeDeclaration[]): _ValidationFailure[] {
        return validateMockStub(value, typeParameters, generics, this.types);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        includeRandomOptionalFields: boolean,
        typeParameters: _UTypeDeclaration[],
        generics: _UTypeDeclaration[],
        randomGenerator: _RandomGenerator
    ): any {
        throw new Error("Not implemented");
    }

    getName(generics: _UTypeDeclaration[]): string {
        return _MOCK_STUB_NAME;
    }
}

export class _UError {
    public readonly name: string;
    public readonly errors: _UUnion;

    constructor(name: string, errors: _UUnion) {
        this.name = name;
        this.errors = errors;
    }
}

export class _DeserializationError extends Error {
    constructor(cause?: Error | string) {
        super(cause instanceof Error ? cause.message : cause);
        if (cause instanceof Error) {
            this.name = cause.name;
            this.stack = cause.stack;
        } else {
            Error.captureStackTrace(this, this.constructor);
        }
    }
}

export class _BinaryEncoderUnavailableError extends Error {}

export class _BinaryEncodingMissing extends Error {
    constructor(key: any) {
        super(`Missing binary encoding for ${String(key)}`);
    }
}

export class _InvalidMessage extends Error {
    constructor(cause?: Error) {
        super(cause ? cause.message : undefined);
        if (cause) {
            this.name = cause.name;
            this.stack = cause.stack;
        }
    }
}

export class _InvalidMessageBody extends Error {}

export class _BinaryEncoding {
    public readonly encodeMap: Map<string, number>;
    public readonly decodeMap: Map<number,string>;
    public readonly checksum: number;

    constructor(binaryEncodingMap: Map<string, number>, checksum: number) {
        this.encodeMap = binaryEncodingMap;
        const decodeList: [number, string][] = [...binaryEncodingMap.entries()].map((e: [string, number]) => [e[1], e[0]]);
        this.decodeMap = new Map(decodeList)
        this.checksum = checksum;
    }
}

export interface _BinaryEncoder {
    encode(message: any[]): any[];
    decode(message: any[]): any[];
}

export class _ServerBinaryEncoder implements _BinaryEncoder {
    private readonly binaryEncoder: _BinaryEncoding;

    constructor(binaryEncoder: _BinaryEncoding) {
        this.binaryEncoder = binaryEncoder;
    }

    encode(message: any[]): any[] {
        return serverBinaryEncode(message, this.binaryEncoder);
    }

    decode(message: any[]): any[] {
        return serverBinaryDecode(message, this.binaryEncoder);
    }
}

export class _ClientBinaryEncoder implements _BinaryEncoder {
    private readonly recentBinaryEncoders: Map<number, _BinaryEncoding>;
    private readonly binaryChecksumStrategy: ClientBinaryStrategy;

    constructor(binaryChecksumStrategy: ClientBinaryStrategy) {
        this.recentBinaryEncoders = new Map<number, _BinaryEncoding>();
        this.binaryChecksumStrategy = binaryChecksumStrategy;
    }

    encode(message: any[]): any[] {
        return clientBinaryEncode(message, this.recentBinaryEncoders, this.binaryChecksumStrategy);
    }

    decode(message: any[]): any[] {
        return clientBinaryDecode(message, this.recentBinaryEncoders, this.binaryChecksumStrategy);
    }
}

export class _MockStub {
    constructor(public readonly whenFunction: string, public readonly whenArgument: Record<string, any>, public readonly thenResult: Record<string, any>,
                public readonly allowArgumentPartialMatch: boolean, public count: number) {}
}

export class _MockInvocation {
    readonly functionName: string;
    readonly functionArgument: Record<string, any>;
    verified: boolean;

    constructor(functionName: string, functionArgument: Record<string, any>) {
        this.functionName = functionName;
        this.functionArgument = functionArgument;
        this.verified = false;
    }
}
