import 'dart:convert';
import 'dart:html';
import 'dart:js_interop';
import 'dart:js_interop_unsafe';

import 'package:node_interop/util.dart';
import 'package:test/test.dart';
import 'package:uapi/uapi.dart';
import 'dart:typed_data';

void main() {
  group('Server', () {
    test('should process request message bytes', () async {
      // Print all files loaded in the browser
      print(window.document.getElementsByTagName('script'));

      // Print the names of the javascript files loaded in the browser
      print(window.document
          .getElementsByTagName('script')
          .map((e) => (e as ScriptElement).src));

      final uapiPseudoJson = [
        {
          "struct.Data": {
            "field": ["boolean"]
          }
        }
      ];
      final uapiJson = jsonEncode(uapiPseudoJson);
      final uapiSchema = UApiSchema.fromJson(uapiJson);

      JSPromise handler(Message requestMessage) {
        return Future.value(Message(JSObject(), JSObject())).toJS;
      }

      final serverOptions = ServerOptions()..authRequired = false;
      final server = Server(uapiSchema, handler.toJS, serverOptions);

      final requestMessageBytes = Uint8List.fromList([1, 2, 3]);
      dynamic request = [
        {},
        {"ping_": {}}
      ];
      dynamic requestBytes = jsonEncode(request);
      final responseBytes = await server.process(requestBytes).toDart;
      if (responseBytes == null) {
        fail('responseBytes is null');
      }
      dynamic response = jsonDecode(utf8.decode(responseBytes.toDart));
      dynamic expectedResponse = [
        {},
        {"Ok_": {}}
      ];
      expect(response, equals(expectedResponse));
    });
  });
}
