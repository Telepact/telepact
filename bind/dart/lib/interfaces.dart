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

class TelepactSchema {
  final b.TelepactSchema telepactSchema;

  TelepactSchema(b.TelepactSchema schema): telepactSchema = schema;

  static TelepactSchema fromJson(String json) {
    final schema = b.TelepactSchema.fromJson(json);
    return TelepactSchema(schema);
  }
}

class RandomGenerator {
  final b.RandomGenerator _randomGenerator;

  RandomGenerator(int collectionLengthMin, int collectionLengthMax)
      : _randomGenerator = b.RandomGenerator(collectionLengthMin, collectionLengthMax);

  void setSeed(int seed) => _randomGenerator.setSeed(seed);
  int nextInt() => _randomGenerator.nextInt();
  int nextIntWithCeiling(int ceiling) => _randomGenerator.nextIntWithCeiling(ceiling);
  bool nextBoolean() => _randomGenerator.nextBoolean();
  String nextString() => _randomGenerator.nextString();
  double nextDouble() => _randomGenerator.nextDouble();
  int nextCollectionLength() => _randomGenerator.nextCollectionLength();
}

class Message {
  Map<String, Object> _headers;
  Map<String, Object> _body;

  Message(Map<String, Object> headers, Map<String, Object> body)
      : _headers = headers,
        _body = body;

  Message.fromJS(b.Message message)
      : _headers = mapJsHeaders(message.headers),
        _body = mapJsBody(message.body);

  static mapJsHeaders(JSAny headers) {
    final h = headers.dartify() as Map<Object?, Object?>;
    return h.cast<String, Object>();
  }

  static mapJsBody(JSAny body) {
    final b = body.dartify()as Map<Object?, Object?>;
    return b.cast<String, Object>();
  }

  b.Message get _message => b.Message(_headers.jsify(), _body.jsify());

  Map<String, Object> get headers => _headers;
  Map<String, Object> get body => _body;
}

class Serializer {
  final b.Serializer _serializer;

  Serializer.fromJS(b.Serializer serializer)
      : _serializer = serializer;

  Uint8List serialize(Message message) => _serializer.serialize(message._message).toDart;
  Message deserialize(Uint8List messageBytes) => Message.fromJS(_serializer.deserialize(messageBytes.toJS));
}

class Client {
  final b.Client _client;

  Client(Future<Message> Function(Message m, Serializer s) adapter, ClientOptions options)
      : _client = initClient(adapter, options);

  static b.Client initClient(Future<Message> Function(Message im, Serializer iis) adapter, ClientOptions options) {
      JSPromise outerAdapter(b.Message om, b.Serializer os) {
        final m = Message.fromJS(om);
        final s = Serializer.fromJS(os);
        return adapter(m, s).then((response) {
          return response._message;
        }).toJS;
      }
      return b.Client(outerAdapter.toJS, options._options);
  }

  Future<Message> request(Message requestMessage) async {
    final response = await _client.request(requestMessage._message).toDart;
    return Message.fromJS(response);
  }
}

class ClientOptions {
  final b.ClientOptions _options;

  ClientOptions()
      : _options = b.ClientOptions();

  set useBinary(bool value) => _options.useBinary = value;

  set alwaysSendJson(bool value) => _options.alwaysSendJson = value;

  set timeoutMsDefault(int value) => _options.timeoutMsDefault = value;

  set localStorageCacheNamespace(String value) => _options.localStorageCacheNamespace = value;
}

class Server {
  final b.Server _server;

  Server(TelepactSchema schema, Future<Message> Function(Message m) handler, ServerOptions options)
      : _server = initServer(schema.telepactSchema, handler, options);

  static b.Server initServer(b.TelepactSchema schema, Future<Message> Function(Message im) handler, ServerOptions options) {
      JSPromise outerHandler(b.Message om) {
        final m = Message.fromJS(om);
        return handler(m).then((response) {
          return response._message;
        }).toJS;
      }
      return b.Server(schema, outerHandler.toJS, options._options);
  }

  Future<Uint8List> process(Uint8List requestMessageBytes) async {
    final response = await _server.process(requestMessageBytes.toJS).toDart;
    return response.toDart;
  }
}

class ServerOptions {
  final b.ServerOptions _options;

  ServerOptions()
      : _options = b.ServerOptions();

  set onError(void Function(JSObject e) value) => _options.onError = value.toJS;

  set onRequest(void Function(JSObject) value) => _options.onRequest = value.toJS;

  set onResponse(void Function(JSObject) value) => _options.onResponse = value.toJS;

  set authRequired(bool value) => _options.authRequired = value;

  set serialization(b.Serialization value) => _options.serialization = value;
}
