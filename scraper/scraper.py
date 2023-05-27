from base64 import b64decode
from json import loads
from logging import getLogger
from os.path import dirname, join, realpath
from sys import argv
from typing import Any

from configuration import parse
from grpc_proto_helper import (
    GOOGLE_PROTOBUF,
    GRPC_MESSAGE_PATTERN,
    HEADERS,
    INHERITS_PATTERN,
    MESSAGE_PATTERN,
    PRELUDE,
    MessageWrapper,
    get_body,
    get_proto_message_namespace_definitions,
)
from js_helper import Parser, get_js_source
from node_helper import NodeExecutor
from requests import post

_JS_FILE_NAME = "output.js"
_RESPONSE_FILE_NAME = "response.bin"


def _get_node_env_path() -> str:
    base = dirname(realpath(__file__))
    NODE_ENV_NAME = "node_execution_env"
    return join(base, NODE_ENV_NAME)


class Scraper:
    def __init__(self, scrape_url: str, js_source_url: str) -> None:
        self.__scrape_url = scrape_url
        js_source = get_js_source(js_source_url)
        self.__js_parser = Parser(js_source)
        self.__logger = getLogger(__name__)

    def scrape(self, response_name: str, payload: bytes) -> dict[str, Any]:
        response = post(url=self.__scrape_url, data=payload, headers=HEADERS)
        self.__logger.info(f"Got response {response} {response.text}")

        type_definitions = self.__js_parser.get_definitions(GRPC_MESSAGE_PATTERN)

        proto_message_namespaces = get_proto_message_namespace_definitions(
            response_name
        )

        inherits_namespaces = self.__js_parser.make_namespace_declarations(
            INHERITS_PATTERN, GOOGLE_PROTOBUF
        )
        message_namespaces = self.__js_parser.make_namespace_declarations(
            MESSAGE_PATTERN, GOOGLE_PROTOBUF
        )
        script_body = get_body(_RESPONSE_FILE_NAME, response_name)

        with open(join(_get_node_env_path(), _JS_FILE_NAME), "w") as f:

            def append_semicolon(line: str) -> str:
                return line + ";\n"

            f.write(PRELUDE)
            f.write(proto_message_namespaces)
            f.write(inherits_namespaces)
            f.write(message_namespaces)
            f.writelines(map(append_semicolon, type_definitions))
            f.write(script_body)

        with open(join(_get_node_env_path(), _RESPONSE_FILE_NAME), "wb") as f:
            message = MessageWrapper(response.content)
            f.write(message.payload)

        node_executor = NodeExecutor(_get_node_env_path())
        string_response = node_executor.execute(_JS_FILE_NAME).decode("utf8")
        return loads(string_response)


if __name__ == "__main__":
    config = parse(argv[1:])
    scraper = Scraper(config.scrape_url, config.js_source_url)
    output = scraper.scrape(config.response_name, config.payload)
    print(output)
