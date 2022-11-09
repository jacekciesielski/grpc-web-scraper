from unittest import TestCase

from grpc_proto_helper import get_proto_message_namespace_definitions, MessageWrapper


class GetProtoMessageNamespaceDefinitionsTest(TestCase):
    def test_Given_a_namespace_Will_create_simple_js_definition(self):
        definitions = get_proto_message_namespace_definitions("proto.ScrapeReply")
        EXPECTED = "proto = {};\n"
        self.assertEqual(EXPECTED, definitions)

    def test_Given_a_few_of_namespaces_Will_create_nested_js_definitions(self):
        definitions = get_proto_message_namespace_definitions(
            "proto.proto.proto.grpc_scrapper.ScrapeReply"
        )
        EXPECTED = "proto = {proto: {proto: {grpc_scrapper: {}}}};\n"
        self.assertEqual(EXPECTED, definitions)


class MessageWrapperTest(TestCase):
    def test_Given_simple_buffer_Will_return_correct_payload(self):
        # fmt: off
        BUFFER = bytes((0x00, # header byte
                        0x00, 0x00, 0x00, 0x03, # message size
                        0x01, 0x02, 0x03, # payload
                        0x00, 0x00, 0x00, 0x04, # blah, blah irrelevant atm
                        ))
        # fmt: on
        message_wrapper = MessageWrapper(BUFFER)
        EXPECTED = bytes((0x01, 0x02, 0x03))
        self.assertEqual(EXPECTED, message_wrapper.payload)

    def test_Given_a_real_long_buffer_Will_return_correct_payload(self):
        # fmt: off
        BUFFER = bytes((0x00, 0x00, 0x00, 0x00, 0x34, 0x08, 0x64, 0x2a, 0x0a, 0x6b, 0x68, 0x43,
                        0x42, 0x63, 0x67, 0x52, 0x56, 0x64, 0x72, 0x52, 0x00, 0x52, 0x02, 0x08,
                        0x01, 0x52, 0x02, 0x08, 0x02, 0x52, 0x02, 0x08, 0x03, 0x52, 0x02, 0x08,
                        0x04, 0x52, 0x02, 0x08, 0x05, 0x52, 0x02, 0x08, 0x06, 0x52, 0x02, 0x08,
                        0x07, 0x52, 0x02, 0x08, 0x08, 0x52, 0x02, 0x08, 0x09))
        # fmt: on
        message_wrapper = MessageWrapper(BUFFER)
        EXPECTED = BUFFER[5:5+0x34]
        self.assertEqual(EXPECTED, message_wrapper.payload)
