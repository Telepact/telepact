import 'package:test/test.dart';
import 'package:uapi/uapi.dart';
import 'dart:typed_data';

void main() {
  group('RandomGenerator', () {
    test('should generate integers within range', () {
      final generator = RandomGenerator(1, 10);
      generator.setSeed(123);
      final value = generator.nextInt();
      expect(value, inInclusiveRange(1, 10));
    });

    test('should generate boolean values', () {
      final generator = RandomGenerator(1, 10);
      generator.setSeed(123);
      final value = generator.nextBoolean();
      expect(value, isA<bool>());
    });
  });

  group('Checksum', () {
    test('should create checksum with value and expiration', () {
      final checksum = Checksum('abc123', 3600);
      expect(checksum.value, 'abc123');
      expect(checksum.expiration, 3600);
    });
  });

  group('DefaultClientBinaryStrategy', () {
    test('should update checksum', () {
      final strategy = DefaultClientBinaryStrategy();
      strategy.updateChecksum('newChecksum');
      final checksums = strategy.getCurrentChecksums();
      expect(checksums, isNotEmpty);
    });
  });

  group('Message', () {
    test('should create message with headers and body', () {
      final message = Message({'header1': 'value1'}, {'bodyKey': 'bodyValue'});
      expect(message.headers['header1'], 'value1');
      expect(message.body['bodyKey'], 'bodyValue');
    });
  });

  group('DefaultSerialization', () {
    test('should serialize and deserialize JSON', () {
      final serialization = DefaultSerialization();
      final message = Message({'header': 'value'}, {'key': 'value'});
      final jsonBytes = serialization.toJson(message);
      final deserializedMessage = serialization.fromJson(jsonBytes);
      expect(deserializedMessage.headers['header'], 'value');
      expect(deserializedMessage.body['key'], 'value');
    });
  });

  group('Client', () {
    test('should send request and receive response', () async {
      final client = Client(null, null);
      final requestMessage = Message({'header': 'value'}, {'key': 'value'});
      final responseMessage = await client.request(requestMessage);
      expect(responseMessage, isA<Message>());
    });
  });

  group('Server', () {
    test('should process request message bytes', () async {
      final server = Server(null, null, null);
      final requestMessageBytes = Uint8List.fromList([1, 2, 3]);
      final responseMessageBytes = await server.process(requestMessageBytes);
      expect(responseMessageBytes, isA<Uint8List>());
    });
  });
}
