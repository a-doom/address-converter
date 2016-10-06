import enchant
import re
import io
import json


class CheckStatus(object):
    MISSPELLING = "misspelling"
    GOOD = "good"
    NOT_FOUND = "not found"
    NOT_WORD = "not word"


class CheckResult(object):
    def __init__(self, status, word_result, word_orig, score):
        """The result of the word check

        Args:
            status: an instance of the class CheckStatus
            word_result: string, a check result
            word_orig: string, an original, checked word
            score: int, the frequency of occurrence of the word in the dictionary
        """
        self.status = status
        self.word_result = word_result
        self.word_orig = word_orig
        self.score = score

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "{0} - {1} - {2}".format(
            self.status,
            self.word_result,
            self.word_orig,
            self.score)

    def __repl__(self):
        return "{0} - {1} - {2}".format(
            self.status,
            self.word_result,
            self.word_orig,
            self.score)

    def is_good(self):
        return self.status == CheckStatus.GOOD

    def is_misspell(self):
        return self.status == CheckStatus.MISSPELLING

    def is_word(self):
        return self.status != CheckStatus.NOT_WORD

    @staticmethod
    def new_not_word(word_orig=None):
        return CheckResult(CheckStatus.NOT_WORD, None, word_orig, 0)

    @staticmethod
    def new_not_found(word_orig=None):
        return CheckResult(CheckStatus.NOT_FOUND, None, word_orig, 0)

    @staticmethod
    def new_good(word, score):
        return CheckResult(CheckStatus.GOOD, word, word, score)


class SpellChecker(object):
    """Class for checking address text

    It splits the text into words and check each of them.
    """
    def __init__(self, enchant_dict, counted_dict):
        """Create SpellChecker

        Args:
            enchant_dict: an instance of enchant.Dict. Need for check spelling
            counted_dict: an instance of a simple Dictionary. It contains all words
                            and the frequency of their occurrence in the addresses.
        """
        assert isinstance(enchant_dict, enchant.Dict)
        assert isinstance(counted_dict, dict)
        self.enchant_dict = enchant_dict
        self.counted_dict = counted_dict
        self._pattern_not_symbol = re.compile(r"[^a-zA-Zа-яА-ЯёЁ]")


    @staticmethod
    def create(enchant_dict_filename=None, counted_dict_filename=None):
        enchant_dict = enchant.request_pwl_dict(enchant_dict_filename)
        with io.open(counted_dict_filename, "r") as input_file:
            counted_dict = json.load(input_file)
        return SpellChecker(enchant_dict, counted_dict)


    def check_words(self, words_list):
        """Take a list of words and check them

        Args:
            words_list: the list of words on the check
        Returns:
            result_list: the list of correct words
        """
        result_list = []
        len_splited_text_iter = iter(range(len(words_list)))
        for i in len_splited_text_iter:
            word_1 = words_list[i]
            cw_1 = self.check_word(words_list[i])

            if len(words_list) - 1 > i:
                cw_2 = self.check_word(words_list[i + 1], True)
                tmp_list = self._check_two_words(cw_1, cw_2)
                if any(tmp_list):
                    result_list.extend(tmp_list)
                    next(len_splited_text_iter)
                    continue
            if not cw_1.is_good() and cw_1.is_word():
                cw_remix_list, cw_remix_list_score = \
                    self._shuffle_symbols(word_1)
                if (cw_remix_list is not None
                        and cw_remix_list_score >= cw_1.score):
                    result_list.extend([cw.word_result
                                        for cw in cw_remix_list])
                    continue
            if cw_1.is_good() or cw_1.is_misspell():
                result_list.append(cw_1.word_result)
        return result_list


    def _check_two_words(self, cw_1, cw_2):
        result_list = []
        if not cw_1.is_word() or not cw_2.is_word():
            return result_list
        cw_max_score = _max_score([cw_1, cw_2])
        cw_join = self.check_word(cw_1.word_orig + cw_2.word_orig, True)
        if (cw_join.is_good()
            and (cw_join.score > cw_max_score
                 or cw_join.word_result == cw_1.word_result
                 or cw_join.word_result == cw_2.word_result)):
            result_list.append(cw_join.word_result)

        elif not cw_1.is_good() or not cw_2.is_word():
            cw_remix_list, cw_remix_list_score = \
                self._shuffle_symbols(cw_1.word_orig, cw_2.word_orig)
            if (cw_remix_list is not None
                    and cw_remix_list_score > cw_max_score):
                result_list.extend([cw.word_result
                                    for cw in cw_remix_list])
        return result_list


    def _shuffle_symbols(self, word_1, word_2=None):
        """Shuffle the letters and looking for the correct words

        One by one rearranges the letters from the second word
        into the first, looking for the pair of the correct words
        with a maximum score.

        Returns:
            result_pair: the list of two correct words
            result_score: the maximum score
        """
        word_2 = word_2 or ""
        result_pair = None
        combined_word = word_1 + word_2
        result_score = 0
        splits = [[combined_word[:i], combined_word[i:]]
                  for i in range(1, len(combined_word))]
        for item in splits:
            cw_0 = self.check_word(item[0], True)
            cw_1 = self.check_word(item[1], True)
            if cw_0.is_good() and cw_1.is_good():
                score = _max_score([cw_0, cw_1])
                if score > result_score:
                    result_pair = [cw_0, cw_1]
                    result_score = score
        return result_pair, result_score


    def check_word(self, word, with_suggestions=False, min_len=2):
        """Check a single word

        Args:
            word: str, a word fo checking
            with_suggestions: bool, use enchant for check spelling
            min_len: int, the minimal length of word, that checked with enchant
        Returns:
            CheckResult class instance
        """
        if (word is None
                or self._pattern_not_symbol.search(word) is not None):
            return CheckResult.new_not_word(word)

        result_status = CheckStatus.GOOD
        result_word = word
        result_score = self.counted_dict.get(word, -1)
        if result_score == -1:
            suggestions = []
            if not with_suggestions and len(word) >= min_len:
                suggestions = self.enchant_dict.suggest(word)
            if any(suggestions):
                result_status = CheckStatus.MISSPELLING
                result_word = max(
                    suggestions,
                    key=lambda s: self.counted_dict.get(s, 0))
            else:
                result_status = CheckStatus.NOT_FOUND
                result_word = None
            result_score = self.counted_dict.get(result_word, 0)
        return CheckResult(result_status, result_word, word, result_score)


def _max_score(check_result):
    """Take a list of CheckResult and calculates the average of scores
    """
    if check_result is None:
        return 0
    if isinstance(check_result, (CheckResult)):
        return check_result.score
    if not isinstance(check_result, (list, tuple)):
        return 0
    scores = [int(res.score)
              for res in check_result
              if isinstance(res, (CheckResult))]
    if not any(scores):
        return 0
    return max(scores)
