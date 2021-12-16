#!/usr/bin/env python3

class Token:
    def __init__(self, word, pos, upos=""):
        self.word = word
        self.pos = pos
        self.upos = upos
