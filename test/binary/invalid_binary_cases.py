cases = {
    'binary': [
        ['\x92\x81\xA4_bin\x91\xd2\x00\x00\x00\x00\x81\x00\x80', [{}, {'_errorParseFailure': {'reasons': ['IncompatibleBinaryEncoding']}}]],
        ['\x80', [{}, {'_errorParseFailure': {'reasons': ['InvalidJson']}}]],
        ['\x92\x81\xA4_bin\x91\xd2\x3C\xC1\x51\x86\x81\x01\x80','\x92\x81\xA4_bin\x91\xce\x3C\xC1\x51\x86\x81\xA2ok\x80'],
        ['\x92\x81\xA4_bin\x91\xd2\x3C\xC1\x51\x86\x81\x0f\x80', [{}, {'_errorParseFailure': {'reasons': ['BinaryDecodeFailure']}}]]
    ]
}
