#!/usr/bin/env python3

import collections


class Text:

    def __init__(self, tokens, text_length, vocabulary_size, frequency_spectrum):
        self.tokens = tokens
        self.text_length = text_length
        self.vocabulary_size = vocabulary_size
        self.frequency_spectrum = frequency_spectrum

    @classmethod
    def from_tokens(cls, tokens):
        """Create Text object from iterable of tokens."""
        text_length = len(tokens)
        frequency_list = collections.Counter(tokens)
        vocabulary_size = len(frequency_list)
        frequency_spectrum = dict(collections.Counter(frequency_list.values()))
        return cls(tokens, text_length, vocabulary_size, frequency_spectrum)
