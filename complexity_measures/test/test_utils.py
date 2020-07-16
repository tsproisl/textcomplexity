#!/usr/bin/env python3

import unittest

from complexity_measures import utils


class TestDisjointWindows(unittest.TestCase):
    def test_disjoint_windows_01(self):
        tokens = "a b c d e f g h i j k".split()
        windows = ["a b c d".split(), "e f g h".split()]
        output = utils.disjoint_windows(tokens, window_size=4, strategy="left")
        self.assertEqual([o.tokens for o in output], windows)

    def test_disjoint_windows_02(self):
        tokens = "a b c d e f g h i j k".split()
        windows = ["d e f g".split(), "h i j k".split()]
        output = utils.disjoint_windows(tokens, window_size=4, strategy="right")
        self.assertEqual([o.tokens for o in output], windows)

    def test_disjoint_windows_03(self):
        tokens = "a b c d e f g h i j k l m n".split()
        windows = ["c d e f g".split(), "h i j k l".split()]
        output = utils.disjoint_windows(tokens, window_size=5, strategy="center")
        self.assertEqual([o.tokens for o in output], windows)

    def test_disjoint_windows_04(self):
        tokens = "a b c d e f g h i j k".split()
        windows = ["a b c".split(), "e f g".split(), "i j k".split()]
        output = utils.disjoint_windows(tokens, window_size=3, strategy="spread")
        self.assertEqual([o.tokens for o in output], windows)


class TestMovingWindows(unittest.TestCase):
    def test_moving_windows_01(self):
        tokens = "a b c d e f g h i j k".split()
        windows = ["a b c d", "b c d e", "c d e f", "d e f g", "e f g h", "f g h i", "g h i j", "h i j k"]
        windows = [t.split() for t in windows]
        output = utils.moving_windows(tokens, window_size=4, step_size=1)
        self.assertEqual([o.tokens for o in output], windows)

    def test_moving_windows_02(self):
        tokens = "a b c d e f g h i j k".split()
        windows = ["a b c d", "c d e f", "e f g h", "g h i j"]
        windows = [t.split() for t in windows]
        output = utils.moving_windows(tokens, window_size=4, step_size=2)
        self.assertEqual([o.tokens for o in output], windows)

    def test_moving_windows_03(self):
        tokens = "a b c d e f g h i j k l".split()
        windows = ["a b c d", "c d e f", "e f g h", "g h i j", "i j k l"]
        windows = [t.split() for t in windows]
        output = utils.moving_windows(tokens, window_size=4, step_size=2)
        self.assertEqual([o.tokens for o in output], windows)
