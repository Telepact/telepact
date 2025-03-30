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

import 'dart:js_interop';
import 'dart:typed_data';

import 'src/bindings.dart' as b;

/// Represents a schema for Telepact, wrapping the underlying binding schema.
class TelepactSchema {
  final b.TelepactSchema telepactSchema;

  /// Constructs a [TelepactSchema] from a binding schema.
  TelepactSchema(b.TelepactSchema schema) : telepactSchema = schema;

  /// Creates a [TelepactSchema] from a JSON string.
  static TelepactSchema fromJson(String json) {
    final schema = b.TelepactSchema.fromJson(json);
    return TelepactSchema(schema);
  }
}

/// Represents a message with headers and body.
class Message {
  Map<String, Object> _headers;
  Map<String, Object> _body;

  /// Constructs a [Message] with the given headers and body.
  Message(Map<String, Object> headers, Map<String, Object> body)
      : _headers = headers,
        _body = body;

  /// Constructs a [Message] from a JavaScript binding message.
  Message.fromJS(b.Message message)
      : _headers = mapJsHeaders(message.headers),
        _body = mapJsBody(message.body);

  /// Maps JavaScript headers to Dart headers.
  static mapJsHeaders(JSAny headers) {
    final h = headers.dartify() as Map<Object?, Object?>;
    return h.cast<String, Object>();
  }

  /// Maps JavaScript body to Dart body.
  static mapJsBody(JSAny body) {
    final b = body.dartify() as Map<Object?, Object?>;
    return b.cast<String, Object>();
  }

  /// Converts the [Message] to its JavaScript binding representation.
  b.Message get _message => b.Message(_headers.jsify(), _body.jsify());

  /// Gets the headers of the message.
  Map<String, Object> get headers => _headers;

  /// Gets the body of the message.
  Map<String, Object> get body => _body;
}

/// A serializer for serializing and deserializing messages.
class Serializer {
  final b.Serializer _serializer;

  /// Constructs a [Serializer] from a JavaScript binding serializer.
  Serializer.fromJS(b.Serializer serializer) : _serializer = serializer;

  /// Serializes a [Message] into a [Uint8List].
  Uint8List serialize(Message message) =>
      _serializer.serialize(message._message).toDart;

  /// Deserializes a [Uint8List] into a [Message].
  Message deserialize(Uint8List messageBytes) =>
      Message.fromJS(_serializer.deserialize(messageBytes.toJS));
}

/// A client for sending requests and receiving responses.
class Client {
  final b.Client _client;

  /// Constructs a [Client] with an adapter function and client options.
  Client(Future<Message> Function(Message m, Serializer s) adapter,
      ClientOptions options)
      : _client = initClient(adapter, options);

  /// Initializes the client with the adapter function and options.
  static b.Client initClient(
      Future<Message> Function(Message im, Serializer iis) adapter,
      ClientOptions options) {
    JSPromise outerAdapter(b.Message om, b.Serializer os) {
      final m = Message.fromJS(om);
      final s = Serializer.fromJS(os);
      return adapter(m, s).then((response) {
        return response._message;
      }).toJS;
    }

    return b.Client(outerAdapter.toJS, options._options);
  }

  /// Sends a request message and receives a response message.
  Future<Message> request(Message requestMessage) async {
    final response = await _client.request(requestMessage._message).toDart;
    return Message.fromJS(response);
  }
}

/// Options for configuring a [Client].
class ClientOptions {
  final b.ClientOptions _options;

  /// Constructs default [ClientOptions].
  ClientOptions() : _options = b.ClientOptions();

  /// Sets whether to use binary serialization.
  set useBinary(bool value) => _options.useBinary = value;

  /// Sets whether to always send JSON.
  set alwaysSendJson(bool value) => _options.alwaysSendJson = value;

  /// Sets the default timeout in milliseconds.
  set timeoutMsDefault(int value) => _options.timeoutMsDefault = value;

  /// Sets the namespace for local storage cache.
  set localStorageCacheNamespace(String value) =>
      _options.localStorageCacheNamespace = value;
}

/// A server for processing requests and sending responses.
class Server {
  final b.Server _server;

  /// Constructs a [Server] with a schema, handler function, and server options.
  Server(TelepactSchema schema, Future<Message> Function(Message m) handler,
      ServerOptions options)
      : _server = initServer(schema.telepactSchema, handler, options);

  /// Initializes the server with the schema, handler function, and options.
  static b.Server initServer(b.TelepactSchema schema,
      Future<Message> Function(Message im) handler, ServerOptions options) {
    JSPromise outerHandler(b.Message om) {
      final m = Message.fromJS(om);
      return handler(m).then((response) {
        return response._message;
      }).toJS;
    }

    return b.Server(schema, outerHandler.toJS, options._options);
  }

  /// Processes a request message and returns the response as a [Uint8List].
  Future<Uint8List> process(Uint8List requestMessageBytes) async {
    final response = await _server.process(requestMessageBytes.toJS).toDart;
    return response.toDart;
  }
}

/// Options for configuring a [Server].
class ServerOptions {
  final b.ServerOptions _options;

  /// Constructs default [ServerOptions].
  ServerOptions() : _options = b.ServerOptions();

  /// Sets the error handler function.
  set onError(void Function(JSObject e) value) => _options.onError = value.toJS;

  /// Sets the request handler function.
  set onRequest(void Function(JSObject) value) =>
      _options.onRequest = value.toJS;

  /// Sets the response handler function.
  set onResponse(void Function(JSObject) value) =>
      _options.onResponse = value.toJS;

  /// Sets whether authentication is required.
  set authRequired(bool value) => _options.authRequired = value;

  /// Sets the serialization method.
  set serialization(b.Serialization value) => _options.serialization = value;
}

/// Options for configuring a [MockServer].
class MockServerOptions {
  final b.MockServerOptions _options;

  /// Constructs default [MockServerOptions].
  MockServerOptions() : _options = b.MockServerOptions();

  /// Sets the error handler function.
  ///
  /// [value] is a function that handles errors represented as [JSObject].
  set onError(void Function(JSObject e) value) => _options.onError = value.toJS;

  /// Enables or disables message response generation.
  ///
  /// [value] determines whether message response generation is enabled.
  set enableMessageResponseGeneration(bool value) =>
      _options.enableMessageResponseGeneration = value;

  /// Enables or disables optional field generation.
  ///
  /// [value] determines whether optional field generation is enabled.
  set enableOptionalFieldGeneration(bool value) =>
      _options.enableOptionalFieldGeneration = value;

  /// Randomizes optional field generation.
  ///
  /// [value] determines whether optional field generation is randomized.
  set randomizeOptionalFieldGeneration(bool value) =>
      _options.randomizeOptionalFieldGeneration = value;

  /// Sets the minimum length for generated collections.
  ///
  /// [value] specifies the minimum length for generated collections.
  set generatedCollectionLengthMin(int value) =>
      _options.generatedCollectionLengthMin = value;

  /// Sets the maximum length for generated collections.
  ///
  /// [value] specifies the maximum length for generated collections.
  set generatedCollectionLengthMax(int value) =>
      _options.generatedCollectionLengthMax = value;
}

/// Represents a mock schema for Telepact, wrapping the underlying binding schema.
class MockTelepactSchema {
  final b.MockTelepactSchema _schema;

  /// Constructs a [MockTelepactSchema] from a binding schema.
  ///
  /// [schema] is the binding schema to wrap.
  MockTelepactSchema(b.MockTelepactSchema schema) : _schema = schema;

  /// Creates a [MockTelepactSchema] from a JSON string.
  ///
  /// [json] is the JSON string representing the schema.
  static MockTelepactSchema fromJson(String json) {
    final schema = b.MockTelepactSchema.fromJson(json);
    return MockTelepactSchema(schema);
  }
}

/// A mock server for processing requests and sending responses.
class MockServer {
  final b.MockServer _server;

  /// Constructs a [MockServer] with a mock schema and options.
  ///
  /// [schema] is the mock schema to use.
  /// [options] are the options for configuring the mock server.
  MockServer(MockTelepactSchema schema, MockServerOptions options)
      : _server = b.MockServer(schema._schema, options._options);

  /// Processes a request message and returns the response as a [Uint8List].
  ///
  /// [messageBytes] is the request message in bytes.
  /// Returns the response message as a [Uint8List].
  Future<Uint8List> process(Uint8List messageBytes) async {
    final response = await _server.process(messageBytes.toJS).toDart;
    return response.toDart;
  }
}
