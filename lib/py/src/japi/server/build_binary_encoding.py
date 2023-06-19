import hashlib
from typing import Dict
from io.github.brenbar.japi import BinaryEncoder, Parser
from io import BytesIO
from java.nio import ByteBuffer
from java.nio.charset import StandardCharsets
from java.util import Map, TreeSet
from java.util.concurrent.atomic import AtomicLong
from java.util.stream import Collectors


def build_binary_encoder(api_description: Dict[str, Parser.Definition]) -> BinaryEncoder:
    all_api_description_keys = TreeSet()

    for entry in api_description.items():
        all_api_description_keys.add(entry.getKey())

        if isinstance(entry.getValue(), Parser.FunctionDefinition):
            f = entry.getValue()
            all_api_description_keys.addAll(f.inputStruct().fields().keySet())
            all_api_description_keys.addAll(f.outputStruct().fields().keySet())
            all_api_description_keys.addAll(f.errors())
        elif isinstance(entry.getValue(), Parser.TypeDefinition):
            t = entry.getValue()
            type_value = t.type()

            if isinstance(type_value, Parser.Struct):
                all_api_description_keys.addAll(type_value.fields().keySet())
            elif isinstance(type_value, Parser.Enum):
                all_api_description_keys.addAll(type_value.cases().keySet())
        elif isinstance(entry.getValue(), Parser.ErrorDefinition):
            e = entry.getValue()
            all_api_description_keys.addAll(e.fields().keySet())

    atomic_long = AtomicLong(0)
    binary_encoding = all_api_description_keys.stream().collect(
        Collectors.toMap(lambda k: k, lambda k: atomic_long.getAndIncrement()))
    final_string = all_api_description_keys.stream().collect(Collectors.joining("\n"))

    try:
        hash = hashlib.sha256(final_string.encode(
            StandardCharsets.UTF_8)).digest()
        buffer = ByteBuffer.wrap(hash)
        binary_hash = buffer.getLong()
    except NoSuchAlgorithmException as e:
        raise RuntimeError(e)

    return BinaryEncoder(binary_encoding, binary_hash)
