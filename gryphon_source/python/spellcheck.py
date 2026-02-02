from os.path import isfile
import re
from spellchecker import SpellChecker
from PySide6.QtCore import QFile, QTextStream, QIODevice, QRegularExpression
from paths_gryphon import SPELLCHECK_WHITELIST_FILENAME
from mp_code_expressions import MP_KEYWORDS, MP_META_SYMBOLS

"""
spellcheck provides singletone global interfaces.

Interfaces:
  * set_checker(whitelist_text) - set the spellchecker given the user's text
  * user_whitelist() - returns _user_whitelist
  * unknown_words(mp_code_text) - returns set of unknown words
  * unknown_words_regex(mp_code_text)
  * is_unknown_word(word)
  * candidate_words(word) - returns list or []
  * deduplicated_user_whitelist()

Internal data:
  * _SPELLCHECK_DICT set by calling _set_checker
"""

_SPELLCHECK_DICT = {"whitelist_text": None, "checker": None}

def _read_user_whitelist():
    if isfile(SPELLCHECK_WHITELIST_FILENAME):
        # use established whitelist
        with open (SPELLCHECK_WHITELIST_FILENAME) as f:
            return f.read()

    # user does not have a whitelist file yet
    return ""

def _write_user_whitelist(whitelist_text):
    with open(SPELLCHECK_WHITELIST_FILENAME, "w", encoding='utf-8') as f:
        f.write(whitelist_text)

def _clean_text(text):
    # replace everything that is not a letter, number, or apostrophe
    # with a space
    text = re.sub(r"[^a-zA-Z0-9']+", " ", text)
    # replace text containing numbers with space
    text = re.sub(r"[a-zA-Z0-9']*\d{1,}[a-zA-Z0-9']*", " ", text)
    # replace short 1 or 2 character long text with space
    text = re.sub(r"\b[a-zA-Z]{1,2}\b", " ", text)
    return text

# return the user whitelist sorted and deduplicated
def _clean_whitelist_text(whitelist_text):
    # prepare a checker
    checker = SpellChecker()

    # add MP keywords and metasymbols
    checker.word_frequency.load_words("|".split(MP_KEYWORDS))
    checker.word_frequency.load_words("|".split(MP_META_SYMBOLS))

    # add resource whitelist
    f = QFile(":/spellcheck_whitelist")
    f.open(QIODevice.ReadOnly | QIODevice.Text)
    checker.word_frequency.load_text(QTextStream(f).readAll())

    deduplicated_words = list(checker.unknown(whitelist_text.split()))
    deduplicated_words.sort(key=str.lower)
    return ' '.join(deduplicated_words)

# set the whitelist text and the checker
def _set_checker(whitelist_text):
    # clean the input so it contains valid words
    whitelist_text = _clean_text(whitelist_text)

    # clean the whitelist so it contains relevant sorted deduplicated words
    whitelist_text = _clean_whitelist_text(whitelist_text)

    # set whitelist text
    _SPELLCHECK_DICT["whitelist_text"] = whitelist_text

    # set the checker
    checker = SpellChecker()

    # add MP keywords and metasymbols
    checker.word_frequency.load_words("|".split(MP_KEYWORDS))
    checker.word_frequency.load_words("|".split(MP_META_SYMBOLS))

    # add resource whitelist
    f = QFile(":/spellcheck_whitelist")
    f.open(QIODevice.ReadOnly | QIODevice.Text)
    checker.word_frequency.load_text(QTextStream(f).readAll())

    # add user's whitelist
    checker.word_frequency.load_text(_SPELLCHECK_DICT["whitelist_text"])

    _SPELLCHECK_DICT["checker"] = checker

# initialize _SPELLCHECK_DICT
_set_checker(_read_user_whitelist())

# set the whitelist text and the checker
def set_checker(whitelist_text):

    # save to file
    _write_user_whitelist(whitelist_text)

    # set the checker
    _set_checker(whitelist_text)

def user_whitelist():
    return _SPELLCHECK_DICT["whitelist_text"]

def unknown_words(mp_code_text):
    text = _clean_text(mp_code_text)
    return _SPELLCHECK_DICT["checker"].unknown(text.split())

def unknown_words_regex(mp_code_text):
    unknown_word_set = unknown_words(mp_code_text)
    unknown_word_text = '|'.join(unknown_word_set)
    regex = QRegularExpression(
              r"(?<=[^a-zA-Z0-9']|^)(%s)(?=[^a-zA-Z0-9']|$)"%unknown_word_text,
              options=QRegularExpression.CaseInsensitiveOption)
    return regex

def is_unknown_word(word):
    return _SPELLCHECK_DICT["checker"].unknown([word])

def candidate_words(unknown_word):
    candidates = _SPELLCHECK_DICT["checker"].candidates(unknown_word)
    if not candidates:
        candidates = set()
    return sorted(candidates)


