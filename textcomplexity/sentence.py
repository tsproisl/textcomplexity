#!/usr/bin/env python3

import functools

from textcomplexity.utils import misc


# -----------------
#  Sentence length
# -----------------
def sentence_length_words(sentences, punctuation):
    """Mean sentence length in words, i.e. excluding punctuation; also
    returns the standard deviation.

    """
    slw = functools.partial(_sentence_length_words, punctuation=punctuation)
    return misc.average_measure(slw, sentences)


def _sentence_length_words(s, punctuation):
    """Sentence length in words."""
    return len([t for t in s if t.pos not in punctuation])


def sentence_length_tokens(sentences):
    """Mean sentence length in tokens, i.e. including punctuation; also
    returns the standard deviation.

    """
    return misc.average_measure(_sentence_length_words, sentences)


def _sentence_length_tokens(s):
    """Sentence length in tokens."""
    return len(s)


def sentence_length_characters(sentences):
    """Mean sentence length in characters; also returns the standard
    deviation. Sentence length in characters is the sum of token
    lengths plus number of token boundaries, i.e. we assume a space
    between all tokens.

    """
    return misc.average_measure(_sentence_length_characters, sentences)


def _sentence_length_characters(s):
    """Sentence length in characters."""
    token_lengths = [len(t.word) for t in s]
    return sum(token_lengths) + len(token_lengths) - 1


# -------------
#  Punctuation
# -------------
def punctuation_per_sentence(sentences, punctuation):
    """Number of punctuation tokens per sentence (according to
    `punctuation`, a set of part-of-speech tags).

    """
    pps = functools.partial(_punctuation_per_sentence, punctuation=punctuation)
    return misc.average_measure(pps, sentences)


def _punctuation_per_sentence(s, punctuation):
    return len([t for t in s if t.pos in punctuation])


def punctuation_per_token(sentences, punctuation):
    """Number of punctuation tokens per token (according to `punctuation`,
    a set of part-of-speech tags).

    """
    punct, tokens = 0, 0
    for s in sentences:
        punct += _punctuation_per_sentence(s, punctuation)
        tokens += len(s)
    return punct / tokens
