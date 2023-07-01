from itertools import chain
from typing import Iterable, Union
from urllib.parse import urlsplit

from regex import DOTALL, Pattern, escape, finditer, sub as re_sub
from requests import get as requests_get


class Parser:
    def __init__(self, js_source: str) -> None:
        self.__js_source = _remove_comments(js_source)

    def get_definitions(self, pattern: Union[str, Pattern]) -> Iterable[str]:
        # Get unique type names
        objects = set(
            map(lambda match: match[0], finditer(pattern, self.__js_source, DOTALL))
        )

        yield from chain.from_iterable(map(self.get_type_definitions, objects))

    def get_type_definitions(self, object_name: str) -> Iterable[str]:
        escaped_name = escape(object_name)
        # This is poor man's lexer and parser. This probably shall be replaced with proper parsing, but it works for
        # now.
        # Escaping {} in the f-string looks so bad. Alternatives are probably even worse.
        # This overly complicated pattern matches functions definitions, arrays and google module inheritance
        # definitions. Those are minimal definitions for a Message implementation in order to work.
        PATTERN = f"((?:{escaped_name}(?:\\s*\\.\\s*[A-Za-z_]\\w*)*\\s*=\\s*(?:[^{{}}=;]*{{(([^{{}}]*)(?:{{(?2)*}})*(?3)*)*+}}|[^{{}}[\\]=;]*\\[(([^\\]]*)(?:\\[(?4)*\\])*(?5)*)*+\\]))|(?:[A-Za-z_]\\w*\\.)+inherits\\(\\s*{escaped_name}\\s*,\\s*(?:[A-Za-z_]\\w*(?:\\.[A-Za-z_]*)*)*\\s*\\))"
        matches = finditer(PATTERN, self.__js_source, DOTALL)
        yield from map(lambda match: match[0], matches)

    def make_namespace_declarations(self, pattern: str, definition: str) -> str:
        namespaces = set(
            map(lambda match: match[0], finditer(pattern, self.__js_source))
        )

        NAMESPACE_DEFINITION = "const {namespace} = {definition};\n"
        filtered_namespaces = filter(
            lambda namespace: namespace != definition, namespaces
        )
        definitions = map(
            lambda namespace: NAMESPACE_DEFINITION.format(
                namespace=namespace, definition=definition
            ),
            filtered_namespaces,
        )
        return "".join(definitions)


def get_js_source(url: str) -> str:
    url_tuple = urlsplit(url)

    if url_tuple.scheme == "file":
        with open(url_tuple.netloc + url_tuple.path) as f:
            return f.read()

    response = requests_get(url)
    return response.text


def _remove_comments(js_source: str) -> None:
    COMMENT_PATTERN = "//[^\\n]*|/\\*.*?\\*/"
    return re_sub(COMMENT_PATTERN, " ", js_source, 0, DOTALL)
