import 'package:node_interop/node.dart';
import 'package:node_interop/util.dart';
import 'dart:typed_data';
import 'package:js/js.dart';

final dynamic _natsPackage = require('nats.ws');
final dynamic _natsConnect = _natsPackage.connect;

@JS()
@anonymous
class ConnectionOptions {
  external factory ConnectionOptions({
    String? servers,
    String? user,
    String? pass,
    String? token,
    bool? noEcho,
    bool? noRandomize,
    bool? pedantic,
    bool? verbose,
    bool? reconnect,
    int? maxReconnectAttempts,
    int? reconnectTimeWait,
    int? reconnectJitter,
    int? reconnectJitterTLS,
    int? pingInterval,
    int? maxPingOut,
    int? timeout,
    bool? waitOnFirstConnect,
    bool? ignoreClusterUpdates,
    String? inboxPrefix,
    bool? ignoreAuthErrorAbort,
    bool? noAsyncTraces,
    bool? resolve,
    TlsOptions? tls,
    Authenticator? authenticator,
    Function? reconnectDelayHandler,
  });
}

@JS()
@anonymous
class TlsOptions {
  external factory TlsOptions({
    bool? handshakeFirst,
    String? certFile,
    String? cert,
    String? caFile,
    String? ca,
    String? keyFile,
    String? key,
  });
}

@JS()
@anonymous
class Authenticator {
  external factory Authenticator({
    String? auth_token,
    String? user,
    String? pass,
    String? nkey,
    String? sig,
    String? jwt,
  });
}

@JS()
@anonymous
class SubscriptionOptions {
  external factory SubscriptionOptions({
    String? queue,
    int? max,
    int? timeout,
    Function? callback,
  });
}

@JS()
class NatsConnection {
  external void publish(String subject, [dynamic data]);
  external Subscription subscribe(String subject, SubscriptionOptions options);
}

@JS()
class Subscription {
  external void unsubscribe([int max]);
  external void drain();
  external bool isDraining();
  external bool isClosed();
}

Future<NatsConnection> connect([ConnectionOptions? options]) {
  return promiseToFuture(_natsConnect(options));
}
