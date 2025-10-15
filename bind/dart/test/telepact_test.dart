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

import 'package:telepact/interfaces.dart';
import 'package:test/test.dart';
import 'package:web/web.dart' as web;

void main() {
  group('Server', () {
    test('cleaner: should work e2e from client to server', () async {
      final telepactPseudoJson = [
        {
          "fn.add": {"x": "integer", "y": "integer"},
          "->": [
            {
              "Ok_": {"result": "integer"}
            }
          ]
        }
      ];
      final telepactJson = jsonEncode(telepactPseudoJson);
      final telepactSchema = TelepactSchema.fromJson(telepactJson);

      Future<Message> handler(Message requestMessage) async {
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
          final response = Message({}, {
            "Ok_": {"result": result}
          });
          print('Created response: ${response.body}');
          return Future.value(response);
        } catch (e) {
          print('Error in handler:');
          print(e);
          return Future.value(Message({}, {}));
        }
      }

      print('Creating DartServerOptions');
      final serverOptions = ServerOptions()..authRequired = false;
      print('DartServerOptions created: $serverOptions');

      print('Creating DartServer');
      final server = Server(telepactSchema, handler, serverOptions);
      print('DartServer created: $server');

      Future<Message> adapter(Message m, Serializer s) async {
        print('Adapter received message: ${m.body}');
        final requestBytes = s.serialize(m);
        print('Serialized requestBytes: ${String.fromCharCodes(requestBytes)}');
        final r = await server.process(requestBytes);
        final responseBytes = r.bytes;
        print('Received responseBytes: ${String.fromCharCodes(responseBytes)}');
        final response = s.deserialize(responseBytes);
        print('Deserialized response: ${response.body}');
        return response;
      }

      print('Creating DartClientOptions');
      final clientOptions = ClientOptions()
        ..useBinary = true
        ..localStorageCacheNamespace = "test";
      print('DartClientOptions created: $clientOptions');

      // Put some data into the local storage to see if it loads in
      final exampleLocalStorageData = {
        "-1337": {"lol": 1, "notreal": 2}
      };
      //final exampleLocalStorageData = {"-2064039486":{"Ok_":0,"api":1,"fn.add":2,"fn.api_":3,"fn.ping_":4,"result":5,"x":6,"y":7}};
      web.window.localStorage.setItem(
          'telepact-api-encoding:test', jsonEncode(exampleLocalStorageData));

      print('Creating DartClient');
      final client = Client(adapter, clientOptions);
      print('DartClient created: $client');

      {
        final request = Message({}, {'fn.ping_': {}});
        print('Created request: ${request.body}');

        var response = await client.request(request);
        print('Received response: ${response.body}');

        Message expectedResponse = Message({
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
        }, {
          "Ok_": {}
        });
        print('Expected response: ${expectedResponse.body}');

        expect(response.headers, equals(expectedResponse.headers));
        expect(response.body, equals(expectedResponse.body));
      }

      {
        final request = Message({}, {
          'fn.add': {'x': 1, 'y': 2}
        });

        var response = await client.request(request);

        print('response: ${response.body}');

        Message expectedResponse = Message({
          '@bin_': [-2064039486]
        }, {
          "Ok_": {'result': 3}
        });

        expect(response.headers, equals(expectedResponse.headers));
        expect(response.body, equals(expectedResponse.body));

        var data =
            web.window.localStorage.getItem('telepact-api-encoding:test');
        print('local-storage: ${data}');
      }

      final mockTelepactSchema = MockTelepactSchema.fromJson(telepactJson);
      final mockServerOptions = MockServerOptions();
      final mockServer = MockServer(mockTelepactSchema, mockServerOptions);

      Future<Message> mockAdapter(Message m, Serializer s) async {
        print('Mock: Adapter received message: ${m.body}');
        final requestBytes = s.serialize(m);
        print(
            'Mock: Serialized requestBytes: ${String.fromCharCodes(requestBytes)}');
        final r = await mockServer.process(requestBytes);
        final responseBytes = r.bytes;
        print(
            'Mock: Received responseBytes: ${String.fromCharCodes(responseBytes)}');
        final response = s.deserialize(responseBytes);
        print('Mock: Deserialized response: ${response.body}');
        return response;
      }

      final mockClient = Client(mockAdapter, clientOptions);

      {
        final request = Message({}, {
          'fn.add': {'x': 1, 'y': 2}
        });

        var response = await mockClient.request(request);

        print('response: ${response.body}');

        var expectedResponseBody = {
          "Ok_": {'result': 2163713}
        };

        expect(response.body, equals(expectedResponseBody));
      }
    });
  });
}
