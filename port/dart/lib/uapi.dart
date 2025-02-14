import 'dart:js_interop';
import 'dart:typed_data';
import 'dart:js';

extension type RandomGenerator._(JSObject _) implements JSObject {
  external factory RandomGenerator(
      int collectionLengthMin, int collectionLengthMax);
  external void setSeed(int seed);
  external int nextInt();
  external int nextIntWithCeiling(int ceiling);
  external bool nextBoolean();
  external String nextString();
  external double nextDouble();
  external int nextCollectionLength();
}

extension type Checksum._(JSObject _) implements JSObject {
  external String value;
  external int expiration;

  external Checksum(String value, int expiration);
}

extension type DefaultClientBinaryStrategy._(JSObject _) implements JSObject {
  external Checksum get primary;
  external Checksum get secondary;

  external factory DefaultClientBinaryStrategy();
  external void updateChecksum(String newChecksum);
  external JSArray<JSNumber> getCurrentChecksums();
}

extension type Message._(JSObject _) implements JSObject {
  external JSObject get headers;
  external JSObject get body;

  external factory Message(JSObject headers, JSObject body);
}

extension type DefaultSerialization._(JSObject _) implements JSObject {
  external factory DefaultSerialization();
  external JSUint8Array toJson(JSAny uapiMessage);
  external JSUint8Array toMsgpack(JSAny uapiMessage);
  external JSAny fromJson(JSUint8Array bytes);
  external JSAny fromMsgpack(JSUint8Array bytes);
}

extension type Serializer._(JSObject _) implements JSObject {
  external factory Serializer(
      DefaultSerialization serializationImpl, JSAny binaryEncoder);
  external JSUint8Array serialize(Message message);
  external Message deserialize(JSUint8Array messageBytes);
}

extension type Client._(JSObject _) implements JSObject {
  external factory Client(
      JSExportedDartFunction adapter, ClientOptions options);
  external JSPromise<Message> request(Message requestMessage);
}

extension type ClientOptions._(JSObject _) implements JSObject {
  external bool get useBinary;
  external bool get alwaysSendJson;
  external int get timeoutMsDefault;
  external DefaultSerialization get serializationImpl;
  external DefaultClientBinaryStrategy get binaryStrategy;

  external factory ClientOptions();
}

extension type Server._(JSObject _) implements JSObject {
  external factory Server(
      UApiSchema uApiSchema, JSFunction handler, ServerOptions options);
  external JSPromise<JSUint8Array> process(JSUint8Array requestMessageBytes);
}

extension type ServerOptions._(JSObject _) implements JSObject {
  external JSFunction get onError;
  external JSFunction get onRequest;
  external JSFunction get onResponse;
  external bool get authRequired;
  external void set authRequired(bool value);
  external DefaultSerialization get serialization;

  external factory ServerOptions();
}

extension type UApiSchema._(JSObject _) implements JSObject {
  external JSArray get original;
  external JSArray get full;
  external JSObject get parsed;
  external JSObject get parsedRequestHeaders;
  external JSObject get parsedResponseHeaders;

  external factory UApiSchema(JSArray original, JSArray full, JSObject parsed,
      JSObject parsedRequestHeaders, JSObject parsedResponseHeaders);
  external static UApiSchema fromJson(String json);
  external static UApiSchema fromFileJsonMap(JSObject fileJsonMap);
  external static UApiSchema fromDirectory(
      String directory, JSAny fs, JSAny path);
}

extension type MockServer._(JSObject _) implements JSObject {
  external factory MockServer(JSAny mockUApiSchema, JSAny options);
  external JSPromise<JSUint8Array> process(JSUint8Array message);
}

extension type MockServerOptions._(JSObject _) implements JSObject {
  external factory MockServerOptions();
  external void setOnError(JSFunction onError);
  external void setEnableMessageResponseGeneration(bool enable);
  external void setEnableOptionalFieldGeneration(bool enable);
  external void setRandomizeOptionalFieldGeneration(bool enable);
  external void setGeneratedCollectionLengthMin(int min);
  external void setGeneratedCollectionLengthMax(int max);
}

extension type MockUApiSchema._(JSObject _) implements JSObject {
  external factory MockUApiSchema(JSAny original, JSAny full, JSAny parsed,
      JSAny parsedRequestHeaders, JSAny parsedResponseHeaders);
  external static MockUApiSchema fromJson(String json);
  external static MockUApiSchema fromFileJsonMap(JSObject fileJsonMap);
  external static MockUApiSchema fromDirectory(
      String directory, JSAny fs, JSAny path);
}

extension type ClientBinaryEncoder._(JSObject _) implements JSObject {
  external factory ClientBinaryEncoder(JSAny binaryChecksumStrategy);
  external JSAny encode(JSAny message);
  external JSAny decode(JSAny message);
}

extension type ServerBinaryEncoder._(JSObject _) implements JSObject {
  external factory ServerBinaryEncoder(JSAny binaryEncoder);
  external JSAny encode(JSAny message);
  external JSAny decode(JSAny message);
}

extension type BinaryEncoding._(JSObject _) implements JSObject {
  external factory BinaryEncoding(JSAny binaryEncodingMap, int checksum);
}

extension type MockInvocation._(JSObject _) implements JSObject {
  external String get functionName;
  external JSAny get functionArgument;
  external bool get verified;

  external factory MockInvocation(String functionName, JSAny functionArgument);
}

extension type MockStub._(JSObject _) implements JSObject {
  external String get whenFunction;
  external JSAny get whenArgument;
  external JSAny get thenResult;
  external bool get allowArgumentPartialMatch;
  external int get count;

  external factory MockStub(String whenFunction, JSAny whenArgument,
      JSAny thenResult, bool allowArgumentPartialMatch, int count);
}

extension type ClientBinaryStrategy._(JSObject _) implements JSObject {
  external factory ClientBinaryStrategy();
}

extension type UApiSchemaFiles._(JSObject _) implements JSObject {
  external JSObject get filenamesToJson;

  external factory UApiSchemaFiles(String directory, JSAny fs, JSAny path);
}

extension type UApiSchemaParseError._(JSObject _) implements JSObject {
  external JSArray get schemaParseFailures;
  external JSAny get schemaParseFailuresPseudoJson;
}

extension type SerializationError._(JSObject _) implements JSObject {}

extension type UApiError._(JSObject _) implements JSObject {}

extension type ValidationFailure._(JSObject _) implements JSObject {
  external String get path;
  external String get reason;
  external JSAny get data;

  external factory ValidationFailure(String path, String reason, JSAny data);
}

extension type InvalidMessage._(JSObject _) implements JSObject {
  external factory InvalidMessage(JSAny cause);
}

extension type InvalidMessageBody._(JSObject _) implements JSObject {
  external factory InvalidMessageBody();
}

extension type BinaryEncoderUnavailableError._(JSObject _) implements JSObject {
  external factory BinaryEncoderUnavailableError();
}

extension type BinaryEncodingMissing._(JSObject _) implements JSObject {
  external factory BinaryEncodingMissing(JSAny key);
}
