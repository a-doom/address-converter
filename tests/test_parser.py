import unittest
import address_converter.parser as parser


class TestParseHouseNums(unittest.TestCase):

    def test_three_pieces(self):
        self.assertEqual(
            parser.parse_house_nums("test 1-2-3, 1-2-a, 1-a-3"),
            {"1-2-3", "1-2-a", "1-a-3"})

    def test_two_pieces(self):
        self.assertEqual(
            parser.parse_house_nums("test 1-2, test!!! 1-a"),
            {"1-2", "1-a"})

    def test_one_piece(self):
        self.assertEqual(
            parser.parse_house_nums("test 1, 12, 1234"),
            {"1", "12"})

    def test_max_element_size(self):
        self.assertEqual(
            parser.parse_house_nums(
                "123-123 234-2345 34-a-3456 456-aa 567-aa-567"),
            {"123-123", "234", "34-a", "456", "567"})

    def test_split_symbols(self):
        self.assertEqual(
            parser.parse_house_nums(
                r"1/1 2\2 3-3 4:4 5.6 7,8 11 q 12w 13 ee"),
            {"1/1", r"2\2", "3-3", "4:4", "5", "6", "7", "8",
             "11 q", "12w", "13"})

    def test_real_addr(self):
        self.assertEqual(
            parser.parse_house_nums(
                "Россия, Набережные Челны,"
                + " Комсомольская набережная, 30, кв 204"),
            {"30", "204"})
