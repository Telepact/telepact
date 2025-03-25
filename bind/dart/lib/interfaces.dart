import 'dart:js_interop';
import 'dart:typed_data';

import 'bindings.dart';

class DartRandomGenerator {
  final RandomGenerator _randomGenerator;

  DartRandomGenerator(int collectionLengthMin, int collectionLengthMax)
      : _randomGenerator = RandomGenerator(collectionLengthMin, collectionLengthMax);

  void setSeed(int seed) => _randomGenerator.setSeed(seed);
  int nextInt() => _randomGenerator.nextInt();
  int nextIntWithCeiling(int ceiling) => _randomGenerator.nextIntWithCeiling(ceiling);
  bool nextBoolean() => _randomGenerator.nextBoolean();
  String nextString() => _randomGenerator.nextString();
  double nextDouble() => _randomGenerator.nextDouble();
  int nextCollectionLength() => _randomGenerator.nextCollectionLength();
}

class DartMessage {
  Map<String, Object> _headers;
  Map<String, Object> _body;

  DartMessage(Map<String, Object> headers, Map<String, Object> body)
      : _headers = headers,
        _body = body;

  DartMessage.fromJS(Message message)
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

  Message get _message => Message(_headers.jsify(), _body.jsify());

  Map<String, Object> get headers => _headers;
  Map<String, Object> get body => _body;
}

class DartSerializer {
  final Serializer _serializer;

  DartSerializer.fromJS(Serializer serializer)
      : _serializer = serializer;

  Uint8List serialize(DartMessage message) => _serializer.serialize(message._message).toDart;
  DartMessage deserialize(Uint8List messageBytes) => DartMessage.fromJS(_serializer.deserialize(messageBytes.toJS));
}

class DartClient {
  final Client _client;

  DartClient(Future<DartMessage> Function(DartMessage m, DartSerializer s) adapter, DartClientOptions options)
      : _client = initClient(adapter, options);

  static Client initClient(Future<DartMessage> Function(DartMessage im, DartSerializer iis) adapter, DartClientOptions options) {
      JSPromise outerAdapter(Message om, Serializer os) {
        final m = DartMessage.fromJS(om);
        final s = DartSerializer.fromJS(os);
        return adapter(m, s).then((response) {
          return response._message;
        }).toJS;
      }
      return Client(outerAdapter.toJS, options._options);
  }

  Future<DartMessage> request(DartMessage requestMessage) async {
    final response = await _client.request(requestMessage._message).toDart;
    return DartMessage.fromJS(response);
  }
}

class DartClientOptions {
  final ClientOptions _options;

  DartClientOptions()
      : _options = ClientOptions();

  set useBinary(bool value) => _options.useBinary = value;

  set alwaysSendJson(bool value) => _options.alwaysSendJson = value;

  set timeoutMsDefault(int value) => _options.timeoutMsDefault = value;

  set binaryStrategy(DartClientBinaryStrategy value) => _options.binaryStrategy = value.toJS();
}

class DartServer {
  final Server _server;

  DartServer(TelepactSchema schema, Future<DartMessage> Function(DartMessage m) handler, DartServerOptions options)
      : _server = initServer(schema, handler, options);

  static Server initServer(TelepactSchema schema, Future<DartMessage> Function(DartMessage im) handler, DartServerOptions options) {
      JSPromise outerHandler(Message om) {
        final m = DartMessage.fromJS(om);
        return handler(m).then((response) {
          return response._message;
        }).toJS;
      }
      return Server(schema, outerHandler.toJS, options._options);
  }

  Future<Uint8List> process(Uint8List requestMessageBytes) async {
    final response = await _server.process(requestMessageBytes.toJS).toDart;
    return response.toDart;
  }
}

class DartServerOptions {
  final ServerOptions _options;

  DartServerOptions()
      : _options = ServerOptions();

  set onError(void Function(JSObject e) value) => _options.onError = value.toJS;

  set onRequest(void Function(JSObject) value) => _options.onRequest = value.toJS;

  set onResponse(void Function(JSObject) value) => _options.onResponse = value.toJS;

  set authRequired(bool value) => _options.authRequired = value;

  set serialization(Serialization value) => _options.serialization = value;
}


abstract class DartClientBinaryStrategy {
  void updateChecksum(int checksum);
  List<int> getCurrentChecksums();

  toJS() {
    JSArray outer() {
      final list = getCurrentChecksums();
      return list.jsify() as JSArray;
    }
    return ClientBinaryStrategy(
      updateChecksum: updateChecksum.toJS,
      getCurrentChecksums: outer.toJS
    );
  }
}