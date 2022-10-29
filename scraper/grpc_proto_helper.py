GOOGLE_PROTOBUF = "jspb"
PRELUDE = f"""const {{readFile}} = require('fs');
const {GOOGLE_PROTOBUF} = require('google-protobuf');
"""


def get_proto_message_namespace_definitions(message_name: str) -> str:
    # The last token is message class itself that will be declared later by JS definitions
    tokens = message_name.split(".")[:-1]
    outmost_namespace = tokens[0]
    inner_namespaces = tokens[1:]
    inner_namespaces_definitions = "".join(
        map(lambda namespace: f"{namespace}: {{", inner_namespaces)
    ) + "}" * len(inner_namespaces)
    namespaces_definitions = f"{outmost_namespace} = {{{inner_namespaces_definitions}}};\n"

    return namespaces_definitions


GRPC_MESSAGE_PATTERN = (
    "proto(?:\\s*\\.\\s*[A-Za-z_]\\w*)+(?=\\s*\\.\\s*deserializeBinary)"
)


INHERITS_PATTERN = "[A-Za-z_]\\w*(?=\\s*\\.\\s*inherits\\s*\\()"
MESSAGE_PATTERN = "[A-Za-z_]\\w*(?=\\s*\\.\\s*Message\\s*\\.\\s*[A-Za-z_])"

HEADERS = {
    "Content-Type": "application/grpc-web+proto",
}


def get_body(file_name: str, class_name: str) -> str:
    body = f"""readFile('{file_name}', (err, data) => {{
console.log(JSON.stringify({class_name}.deserializeBinary(data).toObject()));
}});
"""
    return body


class _BufferReader:
    def __init__(self, buffer: bytes) -> None:
        self.__buffer = buffer
        self.__index = 0

    # turned out unused
    # def read_variant_int(self) -> int:
    #     currently_read = []
    #     while len(currently_read) == 0 or currently_read[-1] & 0b1000_0000:
    #         currently_read.append(int(self.__buffer[self.__index]) & 0b0111_1111)
    #         self.__index += 1
    #     result = 0
    #     # Make it lil endian
    #     for byte, index in zip(currently_read, range(len(currently_read))):
    #         result += byte << index * 7

    #     return result

    def read_int8(self) -> int:
        return self.__read_int_n(size=1)

    def read_int32(self) -> int:
        return self.__read_int_n(size=4)

    def read_byte_array(self, size: int) -> bytes:
        array = self.__buffer[self.__index : self.__index + size]
        self.__index += size

        return array

    def __read_int_n(self, size: int) -> int:
        BYTE_ORDER = "big"
        value = int.from_bytes(
            self.__buffer[self.__index : self.__index + size], BYTE_ORDER
        )
        self.__index += size
        return value


class MessageWrapper:
    def __init__(self, buffer: bytes) -> None:
        buffer_reader = _BufferReader(buffer)
        # Skip unknown int
        buffer_reader.read_int8()
        payload_size = buffer_reader.read_int32()
        self.__payload = buffer_reader.read_byte_array(payload_size)

    @property
    def payload(self) -> bytes:
        return self.__payload
