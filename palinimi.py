#!/usr/bin/env python3
# coding: utf-8
#
# MIT License
#
# Copyright (c) 2024 ShyPiano
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""pali nimi: a tool to generate names

Generate names based on Toki Pona's phonotactics.
Can be used to help name characters, worlds, pets, etc.

This module gives access to the function generate_words, that will return a
list of all valid possible Toki Pona words, restricted to the options given as
argument.
This module also gives access to generators that will yield valid Toki Pona
syllables and words, as well as functions to check whether a string is a valid
Toki Pona syllable or word.

Typical usage example:
  options = PaliNimiGenerationOptions(2, 3)
  words = generate_words(options)
"""
import argparse
import re
from typing import Generator, List

_TOK_LETTERS = "aeijklmnopstuw"
_TOK_VOWELS = "aeiou"
_TOK_CONSONANTS = "jklmnpstw"


def is_valid_tok_syllable(s: str) -> bool:
    """Checks whether a string corresponds to a valid Toki Pona syllable.

    In Toki Pona, syllables take the form (C)V(n), where:
     - (C) is a consonant (optional)
     - V is a vowel
     - (n) is a terminal "n" character, also known as coda nasal (optional)

    Vowels are "a", "e", "i", "o", "u".
    Consonants are "j", "k", "l", "m", "n", "p", "s", "t", "w".

    The syllables "ti", "wo", "wu", and "ji" (alongside their coda nasal
    conterparts) are not valid, despite otherwise adhering to these rules.

    Args:
        s: the string to check.

    Returns:
        True if s corresponds to a valid Toki Pona syllable,
          False otherwise.
    """
    if s.endswith("n"):
        # If s has coda nasal, ignore it.
        # All valid syllables with coda nasal
        # are valid without it, and vice-versa.
        return is_valid_tok_syllable(s[:-1])
    if s in ["ti", "wo", "wu", "ji"]:
        # Fail all forbidden syllables.
        return False
    if len(s) == 2:
        # Check for CV structure.
        return s[0] in _TOK_CONSONANTS and s[1] in _TOK_VOWELS
    if len(s) == 1:
        # Check for V structure.
        return s[0] in _TOK_VOWELS
    return False


def yield_tok_syllables() -> Generator[str, None, None]:
    """Generator for Toki Pona syllables.

    This will yield all valid unique Toki Pona syllables in alphabetical order.
    Once all possible syllables have been generated, it will end.

    Yields:
        Toki Pona syllables, as string, in alphabetical order.
    """
    for ltr in _TOK_LETTERS:
        if ltr in _TOK_VOWELS:
            # Syllabes V and Vn.
            yield ltr
            yield ltr + "n"
        else:
            for v in _TOK_VOWELS:
                s = ltr + v
                if is_valid_tok_syllable(s):
                    # Syllables CV and CVn.
                    yield s
                    yield s + "n"


_TOK_SYLLABLES = list(yield_tok_syllables())


def is_valid_tok_word(w: str) -> bool:
    """Checks whether a string corresponds to a valid Toki Pona word.

    Toki Pona words must:
     - Be composed of valid Toki Pona syllables
     - All syllables, except the first, must be in the format CV(n)
     - Syllables starting with "m" or "n" cannot follow one with coda nasal

    A valid Toki Pona word is not necessarily an existing Toki Pona word!
    This will return True as long as the word follows all listed rules,
    regardless if the word exists or not in the Toki Pona vocabulary.
    An empty string is not considered a word.

    Args:
        w: the string to be checked.

    Returns:
        True if w is a valid Toki Pona word (that is, it follows Toki Pona's
          phonotactics), False otherwise.
    """
    def is_valid_tok_word_r(w: str, start: bool, after_nasal: bool) -> bool:
        if len(w) == 0:
            # We have reached the end of the word!
            # The empty string is not considered a valid word,
            # but otherwise, seeing as we have verified all syllables
            # without finding fault, we can conclude the word is valid.
            return not start
        if w[0] in _TOK_VOWELS and not start:
            # A syllable can only be in the format V(n) at the start.
            return False
        if w[0] in "mn" and after_nasal:
            # A syllable can only start with m/n if
            # the previous syllable didn't have coda nasal.
            return False
        if is_valid_tok_syllable(w[0:1]):
            # Are we looking at a one character long first syllable?
            # If it is a valid syllable, then let's take the
            # hypothesis that the word starts with this syllable and
            # check whether the rest of the word is valid too.
            if is_valid_tok_word_r(w[1:], False, False):
                # If so, then we have determined this is a valid word!
                return True
        if is_valid_tok_syllable(w[0:2]):
            # Are we looking at a two character long first syllable?
            # Same strategy as before...
            if is_valid_tok_word_r(w[2:], False, w[1] == "n"):
                return True
        if is_valid_tok_syllable(w[0:3]):
            # Are we looking at a three character long first syllable?
            # Same strategy as before...
            if is_valid_tok_word_r(w[3:], False, True):
                return True
        # We tried all possible hypothesis, and none returned a valid
        # reading of the word. This is not a valid word.
        return False

    # Recursive implementation - we need to give a couple of initial values
    return is_valid_tok_word_r(w, True, False)


def yield_tok_words(syllable_count: int) -> Generator[str, None, None]:
    """Generator for Toki Pona words.

    This will yield all valid unique Toki Pona words
    with the specified number of syllables in alphabetical order.
    Once all possible words have been generated, it will end.

    syllable_count must be a positive integer.
    ValueError will be raised otherwise.

    Args:
        syllable_count: the number of syllabes the words must have.

    Yields:
        Toki Pona words with syllable_count syllables, as string,
          in alphabetical order.

    Raises:
        ValueError: if syllable_count is not a positive integer.
    """
    def yield_tok_words_r(
            syllable_count: int, start: bool, after_nasal: bool
    ) -> Generator[str, None, None]:
        # Start by picking the syllables that are valid to start this word
        valid_head_syllables = []
        for s in _TOK_SYLLABLES:
            if s[0] in _TOK_VOWELS and not start:
                continue
            if s[0] in "mn" and after_nasal:
                continue
            valid_head_syllables.append(s)

        # If the words we are generating are 1 syllable long, then we can
        # just yield from the list of valid syllables, as they are already
        # sorted alphabetically
        if syllable_count == 1:
            yield from valid_head_syllables
        else:
            # We will generate words by picking a head syllable, and generating
            # the tail of the word using this generator recursively.
            # In order to correctly yield the words in alphabetical order, we
            # must look at a pair of head syllables (C)V and (C)Vn.
            # We will have a generator for each, and while both have not
            # stopped, we will yield the first-in-order generated word, replace
            # it, and repeat. Once a generator has stopped, we can safely
            # exhaust the other and advance to the next pair of head syllables.
            for i in range(0, len(valid_head_syllables), 2):
                syll = valid_head_syllables[i]
                syll_n = valid_head_syllables[i + 1]
                tail_gens = {
                    syll:
                        yield_tok_words_r(syllable_count - 1, False, False),
                    syll_n:
                        yield_tok_words_r(syllable_count - 1, False, True)
                }
                words = {
                    syll:
                        syll + next(tail_gens[syll]),
                    syll_n:
                        syll_n + next(tail_gens[syll_n])
                }
                while True:
                    # We have two possible words to yield.
                    # We want to yield the one that is first, alphabetically.
                    syll_to_use = syll
                    other_syll = syll_n
                    if words[syll_n] < words[syll]:
                        syll_to_use = syll_n
                        other_syll = syll
                    # Note that we don't need to check if the word is valid,
                    # because we know the tail generators can only pick
                    # valid syllables to go after these head ones.
                    yield words[syll_to_use]
                    try:
                        words[syll_to_use] = (
                            syll_to_use + next(tail_gens[syll_to_use]))
                    except StopIteration:
                        # No more words for this head syllable.
                        # We can yield the rest of the words from the
                        # other one and advance to the next pair.
                        yield words[other_syll]
                        for w in tail_gens[other_syll]:
                            yield other_syll + w
                        break

    if syllable_count < 1:
        raise ValueError("syllable_count must be a positive integer")

    # Recursive implementation - we need to give a couple of initial values
    yield from yield_tok_words_r(syllable_count, True, False)


_TOK_NIMI_PU = ["a", "akesi", "ala", "alasa", "ale", "anpa", "ante", "anu",
                "awen", "e", "en", "esun", "ijo", "ike", "ilo", "insa", "jaki",
                "jan", "jelo", "jo", "kala", "kalama", "kama", "kasi", "ken",
                "kepeken", "kili", "kiwen", "ko", "kon", "kule", "kulupu",
                "kute", "la", "lape", "laso", "lawa", "len", "lete", "li",
                "lili", "linja", "lipu", "loje", "lon", "luka", "lukin",
                "lupa", "ma", "mama", "mani", "meli", "mi", "mije", "moku",
                "moli", "monsi", "mu", "mun", "musi", "mute", "nanpa", "nasa",
                "nasin", "nena", "ni", "nimi", "noka", "o", "olin", "ona",
                "open", "pakala", "pali", "palisa", "pan", "pana", "pi",
                "pilin", "pimeja", "pini", "pipi", "poka", "poki", "pona",
                "pu", "sama", "seli", "selo", "seme", "sewi", "sijelo", "sike",
                "sin", "sina", "sinpin", "sitelen", "sona", "soweli", "suli",
                "suno", "supa", "suwi", "tan", "taso", "tawa", "telo", "tenpo",
                "toki", "tomo", "tu", "unpa", "uta", "utala", "walo", "wan",
                "waso", "wawa", "weka", "wile"]
_TOK_NIMI_KU_SULI = ["epiku", "jasima", "kijetesantakalu", "kin", "kipisi",
                     "kokosila", "ku", "lanpan", "leko", "meso", "misikeke",
                     "monsuta", "namako", "oko", "soko", "tonsi"]
_TOK_NIMI_KU_LILI = ["apeja", "ete", "ewe", "isipin", "kamalawala", "kan",
                     "kapesi", "ke", "kese", "kiki", "kulijo", "kuntu",
                     "likujo", "linluwi", "loka", "majuna", "misa", "mulapisu",
                     "neja", "oke", "pake", "pata", "peto", "po", "polinpin",
                     "pomotolo", "powe", "samu", "san", "soto", "taki", "te",
                     "teje", "to", "tuli", "umesu", "unu", "usawi", "wa",
                     "waleja", "wasoweli"]
_TOK_NIMI_SU = ["majuna", "su"]
_TOK_RESERVED_WORDS = ["ju", "lu", "nu", "su", "u"]


class PaliNimiGenerationOptions:
    """Options to restrain Toki Pona word generation.

    Attributes:
        min_syllables:
          the minimum number of syllables the words must have (inclusive).
        max_syllables:
          the maximum number of syllables the words must have (inclusive).
        exclude_pu:
          exclude all nimi pu from the generated words (the 120 words listed
          in Toki Pona: The Language of Good).
        exclude_ku_suli:
          exclude all nimi ku suli from the generated words (the 17 new words
          that are listed in Toki Pona Dictionary as having a frequency index
          of 3 or higher).
        exclude_ku_lili:
          exclude all nimi ku lili from the generated words (the other new
          words that are listed in Toki Pona Dictionary, also referred to as
          nimi ku pi suli ala).
        exclude_su:
          exclude all nimi su from the generated words (the 2 new words used
          in The Wizard Of Oz: Toki Pona Edition).
        exclude_reserved:
          exclude all reserved words from the generated words (the words listed
          in Toki Pona Dictionary as "word reserved for future use by Sonja
          Lang").
        regex:
          the regex pattern the generated words must match.
    """

    def __init__(self,
                 min_syllables: int,
                 max_syllables: int,
                 exclude_pu: bool = False,
                 exclude_ku_suli: bool = False,
                 exclude_ku_lili: bool = False,
                 exclude_su: bool = False,
                 exclude_reserved: bool = False,
                 regex: str = ".*"):
        """Initializes the instance with the given values.

        Args:
            min_syllables:
              the minimum number of syllables the words must have (inclusive).
            max_syllables:
              the maximum number of syllables the words must have (inclusive).
            exclude_pu:
              exclude all nimi pu from the generated words (the 120 words
              listed in Toki Pona: The Language of Good).
            exclude_ku_suli:
              exclude all nimi ku suli from the generated words (the 17 new
              words that are listed in Toki Pona Dictionary as having a
              frequency index of 3 or higher).
            exclude_ku_lili:
              exclude all nimi ku lili from the generated words (the other new
              words that are listed in Toki Pona Dictionary, also referred to
              as nimi ku pi suli ala).
            exclude_su:
              exclude all nimi su from the generated words (the 2 new words
              used in The Wizard Of Oz: Toki Pona Edition).
            exclude_reserved:
              exclude all reserved words from the generated words (the words
              listed in Toki Pona Dictionary as "word reserved for future use
              by Sonja Lang").
            regex:
              the regex pattern the generated words must match.
        """
        self.min_syllables = min_syllables
        self.max_syllables = max_syllables
        self.exclude_pu = exclude_pu
        self.exclude_ku_suli = exclude_ku_suli
        self.exclude_ku_lili = exclude_ku_lili
        self.exclude_su = exclude_su
        self.exclude_reserved = exclude_reserved
        self.regex = re.compile(regex)


def generate_words(options: PaliNimiGenerationOptions) -> List[str]:
    """Lists all possible valid Toki Pona words according to options.

    Args:
        options: an instance of PaliNimiGenerationOptions to constrain the
          results.

    Returns:
        A list of all possible valid Toki Pona words that adhere to the
          constraints imposed by options, sorted alphabetically.

    Raises:
        ValueError: if options present an impossible scenario - i.e.
          options.min_syllables is not a positive integer, or
          options.max_syllables is lesser than options.min_syllables.
    """
    if options.min_syllables < 1:
        raise ValueError("min_syllables must be a positive integer")
    if options.max_syllables < options.min_syllables:
        raise ValueError("max_syllables must not be lesser than min_syllables")
    words = []
    for i in range(options.min_syllables, options.max_syllables + 1):
        for w in yield_tok_words(i):
            if options.exclude_pu and w in _TOK_NIMI_PU:
                continue
            if options.exclude_ku_suli and w in _TOK_NIMI_KU_SULI:
                continue
            if options.exclude_ku_lili and w in _TOK_NIMI_KU_LILI:
                continue
            if options.exclude_su and w in _TOK_NIMI_SU:
                continue
            if options.exclude_reserved and w in _TOK_RESERVED_WORDS:
                continue
            if options.regex.match(w) is not None:
                words.append(w)
    return sorted(words)


if __name__ == "__main__":
    def output(result: List[str]):
        print(*result, sep="\n")

    parser = argparse.ArgumentParser(
        description="Generate words according to Toki Pona phonotactics.")

    parser.add_argument(
        "-p", "--pu", "--exclude-nimi-pu", action="store_true",
        help="Generator will exclude all nimi pu from the results")
    parser.add_argument(
        "-k", "--ku-suli", "--exclude-nimi-ku-suli", action="store_true",
        help="Generator will exclude all nimi ku suli from the results")
    parser.add_argument(
        "-l", "--ku-lili", "--exclude-nimi-ku-lili", action="store_true",
        help="Generator will exclude all nimi ku lili from the results")
    parser.add_argument(
        "-s", "--su", "--exclude-nimi-su", action="store_true",
        help="Generator will exclude all nimi su from the results")
    parser.add_argument(
        "-u", "--reserved", "--exclude-reserved-words", action="store_true",
        help="Generator will exclude all reserved words from the results")

    parser.add_argument(
        "-r", "--regex", type=str, metavar="REGEX", default=".*",
        help="Words will match this regex")

    parser.add_argument(
        "min", type=int,
        help="Minimum amount of syllables the words will have")
    parser.add_argument(
        "max", type=int,
        help="Maximum amount of syllables the words will have")

    args = parser.parse_args()

    options = PaliNimiGenerationOptions(
        args.min, args.max,
        exclude_pu=args.pu,
        exclude_ku_suli=args.ku_suli,
        exclude_ku_lili=args.ku_lili,
        exclude_su=args.su,
        exclude_reserved=args.reserved,
        regex=args.regex)
    output(generate_words(options))
