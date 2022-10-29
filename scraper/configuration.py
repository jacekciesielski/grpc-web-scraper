from argparse import ArgumentParser
from typing import NamedTuple, Sequence, Text


class Config(NamedTuple):
    js_source_url: str
    payload_b64: str
    response_name: str
    scrape_url: str


def parse(args: Sequence[Text]) -> Config:
    parser = ArgumentParser()

    parser.add_argument("--js-source-url", required=True)
    parser.add_argument("--payload-b64", required=True)
    parser.add_argument("--response-name", required=True)
    parser.add_argument("--scrape-url", required=True)

    namespace = parser.parse_args(args)

    return Config(**vars(namespace))
