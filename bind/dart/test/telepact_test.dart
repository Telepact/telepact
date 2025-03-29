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

@TestOn('browser')

import 'dart:convert';
import 'dart:js_interop';

import 'package:telepact/interfaces.dart';
import 'package:test/test.dart';
import 'package:telepact/bindings.dart';
import 'dart:typed_data';
import 'package:web/web.dart' as web;

void main() {
  group('Server', () {
    test('should process request message bytes', () async {
      print('Test started');

      final telepactPseudoJson = [
        {
          "fn.add": {
            "x": ["integer"],
            "y": ["integer"]
          },
          "->": [
            {
              "Ok_": {
                "result": ["integer"]
              }
            }
          ]
        }
      ];
      print("Encoding json");
      final telepactJson = jsonEncode(telepactPseudoJson);
      print('telepactJson: ${telepactJson}');
      final telepactSchema = TelepactSchema.fromJson(telepactJson);
      print('TelepactSchema created: $telepactSchema');

      print('done');

      JSPromise handler(Message requestMessage) {
        print('Handler received requestMessage: ${requestMessage.body.dartify()}');
        final body = requestMessage.body.dartify() as Map<String, Object>;
        print('Parsed body: $body');
        final x = body['x'] as int;
        final y = body['y'] as int;
        print('Extracted x: $x, y: $y');
        final result = x + y;
        print('Computed result: $result');
        final response = Message(
          {}.jsify(),
          {"Ok_": {"result": result}}.jsify()
        );
        print('Created response: ${response.body.dartify()}');
        return Future.value(response).toJS;
      }

      print('Creating ServerOptions');
      final serverOptions = ServerOptions()..authRequired = false;
      print('ServerOptions created: $serverOptions');

      print('Creating Server');
      final server = Server(telepactSchema, handler.toJS, serverOptions);
      print('Server created: $server');

      final requestMessageBytes = Uint8List.fromList([1, 2, 3]);
      print('Request message bytes: $requestMessageBytes');

      JSPromise adapter(Message m, Serializer s) {
        print('Adapter received message: ${m.body.dartify()}');
        final requestBytes = s.serialize(m);
        print('Serialized requestBytes: $requestBytes');
        final responseBytes = server.process(requestBytes).toDart;
        return responseBytes.then((value) {
          print('Received responseBytes: $value');
          final response = s.deserialize(value);
          print('Deserialized response: ${response.body.dartify()}');
          return response.jsify();
        }).toJS;
      }

      print('Creating ClientOptions');
      final clientOptions = ClientOptions()..useBinary = true;
      print('ClientOptions created: $clientOptions');

      print('Creating Client');
      final client = Client(adapter.toJS, clientOptions);
      print('Client created: $client');

      final request = Message(
        {}.jsify(),
        {'fn.ping_': {}}.jsify()
      );
      print('Created request: ${request.body.dartify()}');

      var response = await client.request(request).toDart;
      print('Received response: ${response.body.dartify()}');

      Message expectedResponse = Message(
        {
          '@enc_': {
            'Ok_': 0,
            'api': 1,
            'fn.add': 2,
            'fn.api_': 3,
            'fn.ping_': 4,
            'result': 5,
            'x': 6,
            'y': 7
          },
          '@bin_': [-2064039486]
        }.jsify(),
        {"Ok_": {}}.jsify()
      );
      print('Expected response: ${expectedResponse.body.dartify()}');

      // Print contents and type
      print(response.body.dartify());
      print(response.body.dartify().runtimeType);

      expect(response.headers.dartify(), equals(expectedResponse.headers.dartify()));
      expect(response.body.dartify(), equals(expectedResponse.body.dartify()));

      print('Test completed');
    }, skip: true);

    test('should work e2e from client to server', () async {
      final telepactPseudoJson = [
        {
          "fn.add": {
            "x": ["integer"],
            "y": ["integer"]
          },
          "->": [
            {
              "Ok_": {
                "result": ["integer"]
              }
            }
          ]
        }
      ];
      final telepactJson = jsonEncode(telepactPseudoJson);
      final telepactSchema = TelepactSchema.fromJson(telepactJson);

      JSPromise handler(Message requestMessage) {
        print('Handler received requestMessage: ${requestMessage.body.dartify()}');
        final body = requestMessage.body.dartify() as Map<String, Object>;
        print('Parsed body: $body');
        final x = body['x'] as int;
        final y = body['y'] as int;
        print('Extracted x: $x, y: $y');
        final result = x + y;
        print('Computed result: $result');
        final response = Message(
          {}.jsify(),
          {"Ok_": {"result": result}}.jsify()
        );
        print('Created response: ${response.body.dartify()}');
        return Future.value(response).toJS;
      }

      final serverOptions = ServerOptions()..authRequired = false;
      final server = Server(telepactSchema, handler.toJS, serverOptions);

      JSPromise adapter(Message m, Serializer s) {
        print('Adapter received message: ${m.body.dartify()}');
        final requestBytes = s.serialize(m);
        print('Serialized requestBytes: $requestBytes');
        final responseBytes = server.process(requestBytes).toDart;
        return responseBytes.then((value) {
          print('Received responseBytes: $value');
          final response = s.deserialize(value);
          print('Deserialized response: ${response.body.dartify()}');
          return response.jsify();
        }).toJS;
      }

      final clientOptions = ClientOptions()..useBinary = true;
      final client = Client(adapter.toJS, clientOptions);

      final request = Message(
        {}.jsify(),
        {'fn.ping_': {}}.jsify()
      );
      print('Created request: ${request.body.dartify()}');

      var response = await client.request(request).toDart;
      print('Received response: ${response.body.dartify()}');

      Message expectedResponse = Message(
        {
          '@enc_': {
            'Ok_': 0,
            'api': 1,
            'fn.add': 2,
            'fn.api_': 3,
            'fn.ping_': 4,
            'result': 5,
            'x': 6,
            'y': 7
          },
          '@bin_': [-2064039486]
        }.jsify(),
        {"Ok_": {}}.jsify()
      );
      print('Expected response: ${expectedResponse.body.dartify()}');

      expect(response.headers.dartify(), equals(expectedResponse.headers.dartify()));
      expect(response.body.dartify(), equals(expectedResponse.body.dartify()));
    }, skip: true);

    test('cleaner: should work e2e from client to server', () async {
      final telepactPseudoJson = [
        {
          "fn.add": {
            "x": ["integer"],
            "y": ["integer"]
          },
          "->": [
            {
              "Ok_": {
                "result": ["integer"]
              }
            }
          ]
        }
      ];
      final telepactJson = jsonEncode(telepactPseudoJson);
      final telepactSchema = TelepactSchema.fromJson(telepactJson);

      Future<DartMessage> handler(DartMessage requestMessage) async {
        try {
          print('Handler received requestMessage: ${requestMessage.body}');
          final body = requestMessage.body;
          print('Parsed body: $body');
          final fn = body['fn.add'] as Map<Object?, Object?>;
          final x = fn['x'] as int;
          final y = fn['y'] as int;
          print('Extracted x: $x, y: $y');
          final result = x + y;
          print('Computed result: $result');
          final response = DartMessage(
            {},
            {"Ok_": {"result": result}}
          );
          print('Created response: ${response.body}');
          return Future.value(response);
        } catch (e) {
          print('Error in handler:');
          print(e);
          return Future.value(DartMessage({}, {}));
        }
      }

      print('Creating DartServerOptions');
      final serverOptions = DartServerOptions()..authRequired = false;
      print('DartServerOptions created: $serverOptions');

      print('Creating DartServer');
      final server = DartServer(telepactSchema, handler, serverOptions);
      print('DartServer created: $server');

      Future<DartMessage> adapter(DartMessage m, DartSerializer s) async {
        print('Adapter received message: ${m.body}');
        final requestBytes = s.serialize(m);
        print('Serialized requestBytes: ${String.fromCharCodes(requestBytes)}');
        final responseBytes = await server.process(requestBytes);
        print('Received responseBytes: ${String.fromCharCodes(responseBytes)}');
        final response = s.deserialize(responseBytes);
        print('Deserialized response: ${response.body}');
        return response;
      }

      print('Creating DartClientOptions');
      final clientOptions = DartClientOptions()
        ..useBinary = true
        ..localStorageCacheNamespace="test";
      print('DartClientOptions created: $clientOptions');


      // Put some data into the local storage to see if it loads in
      final exampleLocalStorageData = {"-1337":{"lol": 1, "notreal": 2}};
      //final exampleLocalStorageData = {"-2064039486":{"Ok_":0,"api":1,"fn.add":2,"fn.api_":3,"fn.ping_":4,"result":5,"x":6,"y":7}};
      web.window.localStorage.setItem(
        'telepact-api-encoding:test',
        jsonEncode(exampleLocalStorageData)
      );

      print('Creating DartClient');
      final client = DartClient(adapter, clientOptions);
      print('DartClient created: $client');


      {
        final request = DartMessage(
          {},
          {'fn.ping_': {}}
        );
        print('Created request: ${request.body}');

        var response = await client.request(request);
        print('Received response: ${response.body}');

        DartMessage expectedResponse = DartMessage(
          {
            '@enc_': {
                'Ok_': 0,
                'api': 1,
                'fn.add': 2,
                'fn.api_': 3,
                'fn.ping_': 4,
                'result': 5,
                'x': 6,
                'y': 7
              },            
            '@bin_': [-2064039486]
          },
          {"Ok_": {}}
        );
        print('Expected response: ${expectedResponse.body}');

        expect(response.headers, equals(expectedResponse.headers));
        expect(response.body, equals(expectedResponse.body));
      }

      {
        final request = DartMessage(
          {},
          {
            'fn.add': {
              'x': 1,
              'y': 2
            }
          }
        );

        var response = await client.request(request);

        print('response: ${response.body}');

        var data = web.window.localStorage.getItem('telepact-api-encoding:test');

        DartMessage expectedResponse = DartMessage(
          {
            '@bin_': [-2064039486]
          },
          {"Ok_": {'result': 3}}
        );

        expect(response.headers, equals(expectedResponse.headers));
        expect(response.body, equals(expectedResponse.body));
        
        print('local-storage: ${data}');
      }
    });    

  });
}
