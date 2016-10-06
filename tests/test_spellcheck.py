import unittest
import enchant
from address_converter.spellcheck import (
    CheckResult,
    CheckStatus,
    SpellChecker,
    _max_score)
import os


SPELLCHECK_TEMP_FILENAME = "spellchecker_dict_tmp.txt"


class TestSpellChecker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        counted_dict = {
            "москва": 500, "маршала": 100, "жукова": 50,
            "моск": 10, "ва": 10, "моква": 50, "виноградный": 70,
            "виногрыдный": 1, "московская": 10, "обл": 20,
            "aaabbb": 10, "aaa": 100, "bbb": 100}
        with open(SPELLCHECK_TEMP_FILENAME, "w") as outfile:
            outfile.writelines(line + '\n' for line in counted_dict.keys())
        enchant_dict = enchant.request_pwl_dict(SPELLCHECK_TEMP_FILENAME)
        cls.sh = SpellChecker(
            enchant_dict=enchant_dict,
            counted_dict=counted_dict)

    @classmethod
    def tearDownClass(cls):
        os.remove(SPELLCHECK_TEMP_FILENAME)

    def test_check_word(self):
        self.assertEqual(
            self.sh.check_word("виногрXдный"),
            CheckResult(CheckStatus.MISSPELLING,
                        "виноградный",
                        "виногрXдный",
                        70))
        self.assertEqual(
            self.sh.check_word("виноградный"),
            CheckResult.new_good("виноградный", 70))
        self.assertEqual(
            self.sh.check_word("виногрыдный"),
            CheckResult.new_good("виногрыдный", 1))
        self.assertEqual(
            self.sh.check_word("винXгрыдный"),
            CheckResult(CheckStatus.MISSPELLING,
                        "виногрыдный",
                        "винXгрыдный",
                        1))
        self.assertEqual(
            self.sh.check_word("testtesttest"),
            CheckResult.new_not_found("testtesttest"))
        self.assertEqual(
            self.sh.check_word("123"),
            CheckResult.new_not_word("123"))
        self.assertEqual(
            self.sh.check_word("+++"),
            CheckResult.new_not_word("+++"))
        self.assertEqual(
            self.sh.check_word("виногр999адный"),
            CheckResult.new_not_word("виногр999адный"))
        self.assertEqual(
            self.sh.check_word("виноградный."),
            CheckResult.new_not_word("виноградный."))
        self.assertEqual(
            self.sh.check_word("виноградный "),
            CheckResult.new_not_word("виноградный "))
        self.assertEqual(
            self.sh.check_word(None),
            CheckResult.new_not_word())
        self.assertEqual(
            self.sh.check_word("a"),
            CheckResult.new_not_found("a"))

    def test_remix_words_splited_word(self):
        self.assertEqual(
            self.sh._shuffle_symbols("виноград", "ный"),
            (None, 0))

    def test_remix_words_two_words(self):
        self.assertEqual(
            self.sh._shuffle_symbols("марш", "алажукова"),
            ([CheckResult.new_good("маршала", 100),
              CheckResult.new_good("жукова", 50)],
             100))

    def test_remix_words_min_len(self):
        self.assertEqual(
            self.sh._shuffle_symbols("aa", "a"),
            (None, 0))

    def test_remix_words_wrong_spelling(self):
        self.assertEqual(
            self.sh._shuffle_symbols("марш", "алажуковаX"),
            (None, 0))
        self.assertEqual(
            self.sh._shuffle_symbols("маршала", "жукова3"),
            (None, 0))

    def test_calc_max_score_wrong_type(self):
        self.assertEqual(
            _max_score(None), 0)
        self.assertEqual(
            _max_score(9001), 0)
        self.assertEqual(
            _max_score("test"), 0)

    def test_calc_max_score_wrong_list_type(self):
        self.assertEqual(
            _max_score(["test"]), 0)
        self.assertEqual(
            _max_score([]), 0)

    def test_calc_max_score_single_result(self):
        self.assertEqual(
            _max_score(CheckResult(CheckStatus.GOOD, "test", "test", 10)),
            10)

    def test_calc_max_score_list(self):
        self.assertEqual(
            _max_score(
                [CheckResult.new_good("test", 10),
                 CheckResult.new_good("test", 7)]),
            10)

    def test_calc_max_score_list_remix(self):
        self.assertEqual(
            _max_score(
                [CheckResult(CheckStatus.GOOD, "test", "test", 10),
                 "test"]),
            10)

    def test_check_text_single_word(self):
        self.assertEqual(
            self.sh.check_words(["виногрXдный"]),
            ["виноградный"])

    def test_check_text_two_words(self):
        self.assertEqual(
            self.sh.check_words(["виногрXдный", "москва"]),
            ["виноградный", "москва"])

    def test_check_text_three_words(self):
        self.assertEqual(
            self.sh.check_words(["виногрXдный", "москва", "жукXва"]),
            ["виноградный", "москва", "жукова"])

    def test_check_text_without_words(self):
        self.assertEqual(self.sh.check_words(""), [])


    def test_check_text_splite_words(self):
        self.assertEqual(
            self.sh.check_words(["виногра", "дный", "москва", "жуко", "ва"]),
            ["виноградный", "москва", "жукова"])
        self.assertEqual(
            self.sh.check_words(["виногра", "дный", "моск", "ва", "жуко", "ва"]),
            ["виноградный", "москва", "жукова"])

    def test_check_text_stuck_words(self):
        self.assertEqual(
            self.sh.check_words(["виноградныймосква", "жуковамосква"]),
            ["виноградный", "москва", "жукова", "москва"])

    def test_check_text_long_short(self):
        self.assertEqual(
            self.sh.check_words(["москвава"]),
            ["москва", "ва"])
        self.assertEqual(
            self.sh.check_words(["москва", "ва"]),
            ["москва", "ва"])
        self.assertEqual(
            self.sh.check_words(["москвавX"]),
            ["москва"])

    def test_check_text_four_good_words(self):
        self.assertEqual(
            self.sh.check_words(["московская", "обл", "жукова"]),
            ["московская", "обл", "жукова"])

    def test_check_text_not_split(self):
        self.assertEqual(
            self.sh.check_words(["aaabbb"]),
            ["aaabbb"])
