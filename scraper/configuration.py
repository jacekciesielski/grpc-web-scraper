from argparse import ArgumentParser
from base64 import decodebytes
from typing import NamedTuple, Sequence, Text


class Config(NamedTuple):
    js_source_url: str
    payload: bytes
    response_name: str
    scrape_url: str


def parse(args: Sequence[Text]) -> Config:
    parser = ArgumentParser()

    parser.add_argument("--js-source-url", required=True)
    payload_group = parser.add_mutually_exclusive_group(required=True)
    payload_group.add_argument(
        "--payload-b64", type=_convert_base64_payload, dest="payload"
    )
    payload_group.add_argument(
        "--payload-int-array", type=_convert_byte_int_array, dest="payload"
    )
    parser.add_argument("--response-name", required=True)
    parser.add_argument("--scrape-url", required=True)

    namespace = parser.parse_args(args)

    return Config(**vars(namespace))


def _convert_base64_payload(base64_encoded: str) -> bytes:
    return decodebytes(base64_encoded.encode("ascii"))


def _convert_byte_int_array(int_array: str) -> bytes:
    tokens = int_array.split(",")
    tokens = map(str.strip, tokens)
    tokens = map(int, tokens)
    return bytes(tokens)
