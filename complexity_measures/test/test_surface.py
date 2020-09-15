#!/usr/bin/env python3

import os
import sys
import unittest

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from complexity_measures import surface, text
from complexity_measures.utils import windows


class TestMattr(unittest.TestCase):
    def test_mattr_01(self):
        a = ['b', 'b', 'a', 'b', 'b', 'b', 'b', 'a', 'a', 'a', 'b', 'a', 'b',
             'b', 'a', 'b', 'b', 'a', 'b', 'a', 'b', 'a', 'a', 'a', 'b', 'b',
             'a', 'b', 'a', 'b', 'a', 'a', 'a', 'a', 'b', 'a', 'b', 'b', 'a',
             'a', 'a', 'a', 'a', 'a', 'b', 'b', 'b', 'b', 'b', 'a', 'b', 'b',
             'b', 'b', 'a', 'b', 'b', 'b', 'b', 'b', 'a', 'b', 'b', 'b', 'a',
             'b', 'a', 'a', 'a', 'a', 'a', 'b', 'b', 'a', 'b', 'b', 'a', 'b',
             'b', 'a', 'b', 'a', 'b', 'a', 'a', 'a', 'a', 'a', 'a', 'b', 'a',
             'a', 'b', 'a', 'a', 'a', 'b', 'b', 'a', 'a']
        a = text.Text.from_tokens(a)
        self.assertEqual(surface.mattr(a, 10), 0.2)

    def test_mattr_02(self):
        b = ['d', 'c', 'b', 'i', 'c', 'i', 'i', 'h', 'b', 'a', 'd', 'a', 'i',
             'e', 'b', 'j', 'h', 'd', 'a', 'j', 'j', 'h', 'a', 'f', 'i', 'j',
             'e', 'f', 'e', 'b', 'f', 'b', 'e', 'c', 'd', 'e', 'c', 'f', 'g',
             'j', 'i', 'g', 'h', 'd', 'h', 'i', 'g', 'g', 'h', 'f', 'd', 'c',
             'i', 'j', 'b', 'h', 'g', 'b', 'e', 'e', 'd', 'f', 'h', 'a', 'h',
             'j', 'c', 'a', 'j', 'c', 'h', 'i', 'a', 'f', 'c', 'j', 'g', 'd',
             'e', 'f', 'a', 'c', 'i', 'g', 'c', 'a', 'g', 'b', 'a', 'f', 'e',
             'd', 'g', 'f', 'd', 'b', 'b', 'j', 'e', 'e']
        wins = windows.moving_windows(b, 10)
        results = [surface.type_token_ratio(w) for w in wins]
        mean = sum(results) / len(results)
        b = text.Text.from_tokens(b)
        self.assertAlmostEqual(surface.mattr(b, 10), mean, places=10)
