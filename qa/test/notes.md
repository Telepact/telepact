potential new format:

```json
{
  "_ping": {},
  ".ctx": {
    "Authorization": "Bearer <token>"
  }
}
```

```json

[[]]
[]

42:0
[[42]],
["ida-1"]

42:0, 10:1
[[42, 10]],
["ida-1", true]

42:0, 10:1, 8:2
[
  [42, 10, 8],
  []
],
["ida-1", true, []]

42:0,0 10:0,1 8:0,2 65:1,0
[null, 42, 10, [8, 12]]
["ida-1", true, ["idb-1"]]


[1, 2, [3, 4, 5], 6],
["id-1", false, ["id-2", 0], "world"]

[1, 2, [3, 4, 5], 6],
["id-1", false, ["id-2", 0], "world"]
```

```
b'\x92\x82\xa4_enc\xde\x00\xe0\xa3Any\x00\xa5Array\x01\xb3BinaryDecodeFailure\x02\xa7Boolean\x03\xacErrorExample\x04\xd91ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject\x05\xbdExpectedJsonArrayOfTwoObjects\x06\xb9ExtensionValidationFailed\x07\xafFunctionUnknown\x08\xbaIncompatibleBinaryEncoding\t\xa7Integer\n\xabJsonInvalid\x0b\xa4Null\x0c\xaeNullDisallowed\r\xa6Number\x0e\xb0NumberOutOfRange\x0f\xa6Object\x10\xb3ObjectKeyDisallowed\x11\xd9"ObjectKeyRegexMatchCountUnexpected\x12\xb4ObjectSizeUnexpected\x13\xa2Ok\x14\xa3One\x15\xb8RequiredObjectKeyMissing\x16\xa6String\x17\xa3Two\x18\xaeTypeUnexpected\x19\xabTypeUnknown\x1a\xb0UnionCaseUnknown\x1b\xa7Unknown\x1c\xb8_ErrorInvalidRequestBody\x1d\xbb_ErrorInvalidRequestHeaders\x1e\xb9_ErrorInvalidResponseBody\x1f\xb2_ErrorParseFailure \xad_ErrorUnknown!\xa2aF"\xa6actual#\xa4any!$\xa3api%\xa4arr!&\xa7arrAny!\'\xa7arrArr!(\xa8arrBool!)\xa6arrFn!*\xa7arrInt!+\xabarrNullAny!,\xabarrNullArr!-\xacarrNullBool!.\xaaarrNullFn!/\xabarrNullInt!0\xabarrNullNum!1\xabarrNullObj!2\xadarrNullP2Str!3\xafarrNullP2Union!4\xabarrNullStr!5\xaearrNullStruct!6\xadarrNullUnion!7\xa7arrNum!8\xa7arrObj!9\xa9arrP2Str!:\xacarrP2StrAny!;\xacarrP2StrArr!<\xadarrP2StrBool!=\xabarrP2StrFn!>\xacarrP2StrInt!?\xacarrP2StrNum!@\xacarrP2StrObj!A\xaearrP2StrP2Str!B\xb0arrP2StrP2Union!C\xacarrP2StrStr!D\xafarrP2StrStruct!E\xaearrP2StrUnion!F\xabarrP2Union!G\xabarrPStrAny!H\xabarrPStrArr!I\xacarrPStrBool!J\xaaarrPStrFn!K\xabarrPStrInt!L\xabarrPStrNum!M\xabarrPStrObj!N\xadarrPStrP2Str!O\xafarrPStrP2Union!P\xabarrPStrStr!Q\xaearrPStrStruct!R\xadarrPStrUnion!S\xa7arrStr!T\xaaarrStruct!U\xa9arrUnion!V\xa2bFW\xa5bool!X\xa2cFY\xa5casesZ\xa2dF[\xa5data!\\\xa5dwrap]\xa5enest^\xa5ewrap_\xa8expected`\xa3fn!a\xa7fn._apib\xa8fn._pingc\xabfn._unknownd\xaafn.examplee\xadfn.getBigListf\xa7fn.testg\xa4int!h\xa5itemsi\xa4nestj\xa8nullAny!k\xa8nullArr!l\xa9nullBool!m\xa7nullFn!n\xa8nullInt!o\xa8nullNum!p\xa8nullObj!q\xaanullP2Str!r\xacnullP2Union!s\xa8nullStr!t\xabnullStruct!u\xaanullUnion!v\xa4num!w\xa4obj!x\xa7objAny!y\xa7objArr!z\xa8objBool!{\xa6objFn!|\xa7objInt!}\xabobjNullAny!~\xabobjNullArr!\x7f\xacobjNullBool!\xcc\x80\xaaobjNullFn!\xcc\x81\xabobjNullInt!\xcc\x82\xabobjNullNum!\xcc\x83\xabobjNullObj!\xcc\x84\xadobjNullP2Str!\xcc\x85\xafobjNullP2Union!\xcc\x86\xabobjNullStr!\xcc\x87\xaeobjNullStruct!\xcc\x88\xadobjNullUnion!\xcc\x89\xa7objNum!\xcc\x8a\xa7objObj!\xcc\x8b\xa9objP2Str!\xcc\x8c\xabobjP2Union!\xcc\x8d\xa7objStr!\xcc\x8e\xaaobjStruct!\xcc\x8f\xa9objUnion!\xcc\x90\xa9optional!\xcc\x91\xaaoptional2!\xcc\x92\xa6p2Str!\xcc\x93\xa8p2Union!\xcc\x94\xa8pStrAny!\xcc\x95\xa8pStrArr!\xcc\x96\xa9pStrBool!\xcc\x97\xa7pStrFn!\xcc\x98\xa8pStrInt!\xcc\x99\xacpStrNullAny!\xcc\x9a\xacpStrNullArr!\xcc\x9b\xadpStrNullBool!\xcc\x9c\xabpStrNullFn!\xcc\x9d\xacpStrNullInt!\xcc\x9e\xacpStrNullNum!\xcc\x9f\xacpStrNullObj!\xcc\xa0\xaepStrNullP2Str!\xcc\xa1\xb0pStrNullP2Union!\xcc\xa2\xacpStrNullStr!\xcc\xa3\xafpStrNullStruct!\xcc\xa4\xaepStrNullUnion!\xcc\xa5\xa8pStrNum!\xcc\xa6\xa8pStrObj!\xcc\xa7\xaapStrP2Str!\xcc\xa8\xacpStrP2Union!\xcc\xa9\xa8pStrStr!\xcc\xaa\xabpStrStruct!\xcc\xab\xaapStrUnion!\xcc\xac\xaapUnionAny!\xcc\xad\xaapUnionArr!\xcc\xae\xabpUnionBool!\xcc\xaf\xa9pUnionFn!\xcc\xb0\xaapUnionInt!\xcc\xb1\xaepUnionNullAny!\xcc\xb2\xaepUnionNullArr!\xcc\xb3\xafpUnionNullBool!\xcc\xb4\xadpUnionNullFn!\xcc\xb5\xaepUnionNullInt!\xcc\xb6\xaepUnionNullNum!\xcc\xb7\xaepUnionNullObj!\xcc\xb8\xb0pUnionNullP2Str!\xcc\xb9\xb2pUnionNullP2Union!\xcc\xba\xaepUnionNullStr!\xcc\xbb\xb1pUnionNullStruct!\xcc\xbc\xb0pUnionNullUnion!\xcc\xbd\xaapUnionNum!\xcc\xbe\xaapUnionObj!\xcc\xbf\xacpUnionP2Str!\xcc\xc0\xaepUnionP2Union!\xcc\xc1\xaapUnionStr!\xcc\xc2\xadpUnionStruct!\xcc\xc3\xacpUnionUnion!\xcc\xc4\xa4path\xcc\xc5\xa6pdStr!\xcc\xc6\xa8property\xcc\xc7\xa6reason\xcc\xc8\xa7reasons\xcc\xc9\xa5regex\xcc\xca\xa8required\xcc\xcb\xa4str!\xcc\xcc\xa7struct!\xcc\xcd\xaastruct.Big\xcc\xce\xafstruct.ExStruct\xcc\xcf\xacstruct.Value\xcc\xd0\xbdstruct._BodyValidationFailure\xcc\xd1\xbfstruct._HeaderValidationFailure\xcc\xd2\xaestruct<1>.PStr\xcc\xd3\xafstruct<1>.PdStr\xcc\xd4\xafstruct<2>.P2Str\xcc\xd5\xa6union!\xcc\xd6\xadunion.ExUnion\xcc\xd7\xd9"union._BodyValidationFailureReason\xcc\xd8\xd9$union._HeaderValidationFailureReason\xcc\xd9\xb3union._ParseFailure\xcc\xda\xabunion._Type\xcc\xdb\xafunion<1>.PUnion\xcc\xdc\xb0union<2>.P2Union\xcc\xdd\xa6value!\xcc\xde\xa4wrap\xcc\xdf\xa4_bin\x91\xd2\x93\x11\x18l\x81\x14\x80'
```
