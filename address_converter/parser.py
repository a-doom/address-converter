import re
import io
import json


def parse_address_names(text, min_word_len=3):
    assert isinstance(text, str)
    splited_text = re.findall(
        r"([а-яА-ЯёЁa-zA-Z]+|[\d]+|[^а-яА-ЯёЁa-zA-Z0-9 ]+)",
        text)
    return [word for word in splited_text
            if len(word) > min_word_len]


def parse_house_nums(text):
    """Find matching house numbers

    Possible matchings:
        n   - number {1-3};
        l   - literal{1});
        -   - any Non-alphanumeric character.

        n-n-n     n-n-l   n-l-n
        n-n       n-l
        n

    Result:
        nums: the set of matched house numbers
    """
    assert isinstance(text, str)
    text = text.lower()
    main_number = r"[0-9]{1,3}"
    add_number = r"[\/\\\-:]+[0-9]{1,3}"
    add_symb = r"[ \/\\\-:]?[a-zA-Zа-яА-ЯёЁ]"
    patterns_list = [
        re.compile(r"\b(" + main_number + add_number + add_number + r")\b"),
        re.compile(r"\b(" + main_number + add_number + add_symb + r")\b"),
        re.compile(r"\b(" + main_number + add_symb + add_number + r")\b"),
        re.compile(r"\b(" + main_number + add_number + r")\b"),
        re.compile(r"\b(" + main_number + add_symb + r")\b"),
        re.compile(r"\b(" + main_number + r")\b")]

    nums = set()
    for pattern in patterns_list:
        digits_list = pattern.findall(text)
        nums |= set(digits_list)
        text = re.sub(pattern, " ", text)
    return nums


def parse_postcode(text):
    assert isinstance(text, str)
    postcodes = re.findall(r"(\d{6})", text)
    return postcodes


def clean_address_names_list(addr_objects, stop_words):
    stop_words = stop_words
    return [word for word in addr_objects if word not in stop_words]


def create_stop_words_list(stop_words_list_filename):
    assert isinstance(stop_words_list_filename, str)
    with io.open(stop_words_list_filename, "r") as input_file:
        return json.load(input_file)
