from unittest import TestCase


from js_helper import Parser
from grpc_proto_helper import GRPC_MESSAGE_PATTERN, MESSAGE_PATTERN


SIMPLE_CLASS_NAME = "proto.ScrapeReply"


class JsHelperParserTest(TestCase):
    def test_When_given_simple_method_Will_find_it(self):
        SOURCE = """proto.ScrapeReply.deserializeBinary = function (param) {
  body;
}"""
        sut = Parser(SOURCE)
        definitions = list(sut.get_type_definitions(SIMPLE_CLASS_NAME))
        self.assertEqual([SOURCE], definitions)

    def test_When_given_simple_method_no_whitespace_Will_find_it(self):
        SOURCE = "proto.ScrapeReply.deserializeBinary=function(param){body;}"
        sut = Parser(SOURCE)
        definitions = list(sut.get_type_definitions(SIMPLE_CLASS_NAME))
        self.assertEqual([SOURCE], definitions)

    def test_When_given_simple_method_insane_spaces_Will_find_it(self):
        SOURCE = """proto.ScrapeReply.deserializeBinary

=     \t                              function (param) {
  body;
}"""

        sut = Parser(SOURCE)
        definitions = list(sut.get_type_definitions(SIMPLE_CLASS_NAME))
        self.assertEqual([SOURCE], definitions)

    def test_When_given_simple_method_with_comments_Will_find_it(self):
        SOURCE = """proto.ScrapeReply.deserializeBinary = /* inline comment */ function (param) {
// single line comment
/*
multiline comment
*/
// /* trolololo comment
/* // another trololo comment */
  body;
}"""
        EXPECTED = """proto.ScrapeReply.deserializeBinary =   function (param) {
 
 
 
 
  body;
}"""
        sut = Parser(SOURCE)
        definitions = list(sut.get_type_definitions(SIMPLE_CLASS_NAME))
        self.assertEqual([EXPECTED], definitions)

    def test_When_given_a_method_with_inner_scope_Will_find_it(self):
        SOURCE = """proto.ScrapeReply.deserializeBinary = function [] {
  body;
    for() {
      body;
    }
}"""
        sut = Parser(SOURCE)
        definitions = list(sut.get_type_definitions(SIMPLE_CLASS_NAME))
        self.assertEqual([SOURCE], definitions)

    def test_When_given_a_method_with_a_lot_of_inner_scope_Will_find_it(self):
        SOURCE = """proto.ScrapeReply.deserializeBinary = function [] {
  body;
    for() {
      body;
      for() {
      body;
        for() {
          body;
          for() {
            body;
          }
          for() {
            body;
          }
          for() {
            body;
          }
        }
      }
    }
}"""
        sut = Parser(SOURCE)
        definitions = list(sut.get_type_definitions(SIMPLE_CLASS_NAME))
        self.assertEqual([SOURCE], definitions)

    def test_When_given_method_name_matching_unescaped_pattern_Will_not_find_it(self):
        SOURCE = """protoxScrapeReply.deserializeBinary = function (param) {
  body;
}"""
        sut = Parser(SOURCE)
        definitions = list(sut.get_type_definitions(SIMPLE_CLASS_NAME))
        self.assertEqual([], definitions)

    def test_Given_simple_array_Will_find_it(self):
        SOURCE = "proto.ScrapeReply.repeatedFields_ = [10]"
        sut = Parser(SOURCE)
        definitions = list(sut.get_type_definitions(SIMPLE_CLASS_NAME))
        self.assertEqual([SOURCE], definitions)

    def test_Given_array_no_whitespace_Will_find_it(self):
        SOURCE = "proto.ScrapeReply.repeatedFields_=[10]"
        sut = Parser(SOURCE)
        definitions = list(sut.get_type_definitions(SIMPLE_CLASS_NAME))
        self.assertEqual([SOURCE], definitions)

    def test_Given_array_weird_whitespace_Will_find_it(self):
        SOURCE = """proto.ScrapeReply.repeatedFields_
 = \t                  [10]"""
        sut = Parser(SOURCE)
        definitions = list(sut.get_type_definitions(SIMPLE_CLASS_NAME))
        self.assertEqual([SOURCE], definitions)

    def test_When_given_many_objects_and_methods_Will_return_all(self):
        METHODS = [
            "proto.ScrapeReply = function( ){blah; blah;}",
            "goog.inherits(proto.ScrapeReply, jsbp.Message)",
            "proto.ScrapeReply.deserializeBinary = function(data) {data; data;}",
            "proto.ScrapeReply.repeatedFields_ = [10]",
            "proto.ScrapeReply.foo = function(errr) {body; body;}",
            "proto.ScrapeRequest = function( ){blah; blah;}",
            "proto.ScrapeRequest.repeatedFields_ = [10]",
            "goog.inherits(proto.ScrapeRequest, jspb.Message)",
            "proto.ScrapeRequest.deserializeBinary = function(data) {data; data;}",
            "proto.ScrapeRequest.foo = function(errr) {body; body;}",
        ]
        source = "".join(map(lambda line: line + ";\n", METHODS))
        sut = Parser(source)
        definitions = list(sut.get_definitions(GRPC_MESSAGE_PATTERN))

        # The order is not deterministic. Probably because of the fact that elements in set are not kept in
        # determinicstic order in js_helper.Parser.get_definitions. However it will work as long as order of method
        # definitions is kept for a class
        ALTERNATIVE_METHODS = METHODS[5:] + METHODS[:5]
        result = METHODS == definitions or ALTERNATIVE_METHODS == definitions
        assert result, f"Got {definitions}"
        self.assertTrue(result)

    def test_When_given_many_objects_with_comments_and_methods_Will_return_only_not_in_comment(
        self,
    ):
        METHODS = [
            "proto.ScrapeReply = function( ){blah; blah;}",
            "goog.inherits(proto.ScrapeReply, jsbp.Message)",
            "proto.ScrapeReply./* comment */deserializeBinary = function(data) {data; data;}",
            "proto.ScrapeReply./* comment */anArray = [10 /*]*/, 11, 23] //",
            "proto.ScrapeReply.foo = function(errr) {body; body;}",
            "proto.ScrapeRequest = function( ){blah; blah;}",
            "goog.inherits(proto.ScrapeRequest, jspb.Message)",
            "proto.ScrapeRequest/*.deserializeBinary*/ = function(data) {data; data;}",
            "proto.ScrapeRequest.foo = function(errr) {body; body;}",
        ]
        EXPECTED = [
            "proto.ScrapeReply = function( ){blah; blah;}",
            "goog.inherits(proto.ScrapeReply, jsbp.Message)",
            "proto.ScrapeReply. deserializeBinary = function(data) {data; data;}",
            "proto.ScrapeReply. anArray = [10  , 11, 23]",
            "proto.ScrapeReply.foo = function(errr) {body; body;}",
        ]
        source = "".join(map(lambda line: line + ";\n", METHODS))
        sut = Parser(source)
        definitions = list(sut.get_definitions(GRPC_MESSAGE_PATTERN))

        self.assertEqual(EXPECTED, definitions)

    def test_When_given_unknown_message_namespace_Will_make_correct_namespace_definition(self):
        REPLACEMENT = "replacement"
        SOURCE = (
            "o.Message.deserializeInt(blah blah);\nn.Message.deserializeInt(blah blah);"
        )
        EXPECTED_LINES = [f"const n = {REPLACEMENT};\n", f"const o = {REPLACEMENT};\n"]

        sut = Parser(SOURCE)
        declarations = sut.make_namespace_declarations(MESSAGE_PATTERN, REPLACEMENT)
        # The order is not deterministic. Again.
        result = (
            EXPECTED_LINES[0] + EXPECTED_LINES[1] == declarations
            or EXPECTED_LINES[1] + EXPECTED_LINES[0] == declarations
        )

        assert result, f"Got {declarations}"
