#!/usr/bin/env python3

import collections


class Text:

    def __init__(self, tokens, tags, text_length, vocabulary_size, frequency_list, frequency_spectrum):
        self.tokens = tokens
        self.tags = tags
        self.text_length = text_length
        self.vocabulary_size = vocabulary_size
        self.frequency_list = frequency_list
        self.frequency_spectrum = frequency_spectrum

    @classmethod
    def from_tokens(cls, tokens):
        """Create Text object from iterable of tokens, i.e. named tuples
        (word, pos).

        """
        toks = [t.word for t in tokens]
        tags = [t.pos for t in tokens]
        text_length = len(tokens)
        frequency_list = collections.Counter(toks)
        vocabulary_size = len(frequency_list)
        frequency_spectrum = dict(collections.Counter(frequency_list.values()))
        return cls(toks, tags, text_length, vocabulary_size, frequency_list, frequency_spectrum)
