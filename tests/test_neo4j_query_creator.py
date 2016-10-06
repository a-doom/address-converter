import unittest
from address_converter.neo4j_query_creator import (
    _create_mix_addr_query)


class TestCreateMixAddrQuery(unittest.TestCase):

    def test_check_one_node_one_word(self):
        self.assertEqual(
            _create_mix_addr_query(["a"], 1, 0, "a", "p", True),
            "(a0.p = 'a')")

    def test_check_one_node_two_word(self):
        self.assertEqual(
            _create_mix_addr_query(["a", "b"], 1, 0, "a", "p", True),
            "(a0.p = 'a'\n\t OR a0.p = 'b')")

    def test_check_two_node_one_word(self):
        self.assertEqual(
            _create_mix_addr_query(["a"], 2, 0, "a", "p"), "", True)

    def test_check_two_node_two_word(self):
        self.assertEqual(
            _create_mix_addr_query(["a", "b"], 2, 0, "a", "p", True),
            "(a0.p = 'a'\n\t\tAND (a1.p = 'b')\n\t OR "
            + "a0.p = 'b'\n\t\tAND (a1.p = 'a'))")

    def test_check_two_node_two_word_no_tabs(self):
        self.assertEqual(
            _create_mix_addr_query(["a", "b"], 2, 0, "a", "p", False),
            "(a0.p = 'a' AND (a1.p = 'b') OR "
            + "a0.p = 'b' AND (a1.p = 'a'))")
