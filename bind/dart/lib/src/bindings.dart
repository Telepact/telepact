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
}

extension type Message._(JSObject _) implements JSObject {
  external JSAny get headers;
  external JSAny get body;

  external factory Message(JSAny? headers, JSAny? body);
}

extension type Response._(JSObject _) implements JSObject {
  external JSUint8Array get bytes;
  external JSAny get headers;

  external factory Response(JSUint8Array bytes, JSAny? headers);
}

extension type Serialization._(JSObject _) implements JSObject {
  external JSUint8Array toJson(JSAny telepactMessage);
  external JSUint8Array toMsgpack(JSAny telepactMessage);
  external JSAny fromJson(JSUint8Array bytes);
  external JSAny fromMsgpack(JSUint8Array bytes);
}

extension type Serializer._(JSObject _) implements JSObject {
  external factory Serializer(
      Serialization serializationImpl, JSAny binaryEncoder);
  external JSUint8Array serialize(Message message);
  external Message deserialize(JSUint8Array messageBytes);
}

extension type Client._(JSObject _) implements JSObject {
  external factory Client(JSFunction adapter, ClientOptions options);
  external JSPromise<Message> request(Message requestMessage);
}

extension type ClientOptions._(JSObject _) implements JSObject {
  external bool get useBinary;
  external bool get alwaysSendJson;
  external int get timeoutMsDefault;
  external Serialization get serializationImpl;
  external String get localStorageCacheNamespace;

  external void set useBinary(bool value);
  external void set alwaysSendJson(bool value);
  external void set timeoutMsDefault(int value);
  external void set serializationImpl(Serialization value);
  external void set localStorageCacheNamespace(String value);

  external factory ClientOptions();
}

extension type Server._(JSObject _) implements JSObject {
  external factory Server(
      TelepactSchema telepactSchema, JSFunction handler, ServerOptions options);
  external JSPromise<Response> process(JSUint8Array requestMessageBytes);
}

extension type ServerOptions._(JSObject _) implements JSObject {
  external JSFunction get onError;
  external JSFunction get onRequest;
  external JSFunction get onResponse;
  external bool get authRequired;
  external Serialization get serialization;

  external void set onError(JSFunction onError);
  external void set onRequest(JSFunction onRequest);
  external void set onResponse(JSFunction onResponse);
  external void set authRequired(bool authRequired);
  external void set serialization(Serialization serialization);

  external factory ServerOptions();
}

extension type MockServer._(JSObject _) implements JSObject {
  external factory MockServer(JSAny mockTelepactSchema, JSAny options);
  external JSPromise<Response> process(JSUint8Array message);
}

extension type MockServerOptions._(JSObject _) implements JSObject {
  external factory MockServerOptions();
  external JSFunction get onError;
  external bool get enableMessageResponseGeneration;
  external bool get enableOptionalFieldGeneration;
  external bool get randomizeOptionalFieldGeneration;
  external int get generatedCollectionLengthMin;
  external int get generatedCollectionLengthMax;
  external void set onError(JSFunction onError);
  external void set enableMessageResponseGeneration(bool enable);
  external void set enableOptionalFieldGeneration(bool enable);
  external void set randomizeOptionalFieldGeneration(bool enable);
  external void set generatedCollectionLengthMin(int min);
  external void set generatedCollectionLengthMax(int max);
}

extension type MockTelepactSchema._(JSObject _) implements JSObject {
  external factory MockTelepactSchema(JSAny original, JSAny full, JSAny parsed,
      JSAny parsedRequestHeaders, JSAny parsedResponseHeaders);
  external static MockTelepactSchema fromJson(String json);
}

extension type TelepactSchemaParseError._(JSObject _) implements JSObject {
  external JSArray get schemaParseFailures;
  external JSAny get schemaParseFailuresPseudoJson;
}

extension type SerializationError._(JSObject _) implements JSObject {}

extension type TelepactError._(JSObject _) implements JSObject {}
