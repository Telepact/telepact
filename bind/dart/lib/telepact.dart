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

@JS('Telepact')
library;

import 'dart:js_interop';

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
  external JSAny? get headers;
  external JSAny? get body;

  external factory Message(JSAny? headers, JSAny? body);
}

extension type DefaultSerialization._(JSObject _) implements JSObject {
  external factory DefaultSerialization();
  external JSUint8Array toJson(JSAny telepactMessage);
  external JSUint8Array toMsgpack(JSAny telepactMessage);
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
      JSFunction adapter, ClientOptions options);
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
      TelepactSchema telepactSchema, JSFunction handler, ServerOptions options);
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

extension type TelepactSchema._(JSObject _) implements JSObject {
  external JSArray get original;
  external JSArray get full;
  external JSObject get parsed;
  external JSObject get parsedRequestHeaders;
  external JSObject get parsedResponseHeaders;

  external factory TelepactSchema(
      JSArray original,
      JSArray full,
      JSObject parsed,
      JSObject parsedRequestHeaders,
      JSObject parsedResponseHeaders);
  external static TelepactSchema fromJson(String json);
  external static TelepactSchema fromFileJsonMap(JSObject fileJsonMap);
  external static TelepactSchema fromDirectory(
      String directory, JSAny fs, JSAny path);
}

extension type MockServer._(JSObject _) implements JSObject {
  external factory MockServer(JSAny mockTelepactSchema, JSAny options);
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

extension type MockTelepactSchema._(JSObject _) implements JSObject {
  external factory MockTelepactSchema(JSAny original, JSAny full, JSAny parsed,
      JSAny parsedRequestHeaders, JSAny parsedResponseHeaders);
  external static MockTelepactSchema fromJson(String json);
  external static MockTelepactSchema fromFileJsonMap(JSObject fileJsonMap);
  external static MockTelepactSchema fromDirectory(
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

extension type TelepactSchemaFiles._(JSObject _) implements JSObject {
  external JSObject get filenamesToJson;

  external factory TelepactSchemaFiles(String directory, JSAny fs, JSAny path);
}

extension type TelepactSchemaParseError._(JSObject _) implements JSObject {
  external JSArray get schemaParseFailures;
  external JSAny get schemaParseFailuresPseudoJson;
}

extension type SerializationError._(JSObject _) implements JSObject {}

extension type TelepactError._(JSObject _) implements JSObject {}

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
