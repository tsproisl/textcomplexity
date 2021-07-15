#!/usr/bin/env python3

import collections
import warnings

from textcomplexity.text import Text


def disjoint_windows(tokens, window_size, strategy="spread"):
    """Yield disjoint windows of text. If the last window would be smaller
    than window_size, the position of the windows is determined
    according to strategy.

    strategy="left": Move the windows to the left, omitting tokens at
    the end of the text.

    strategy="right": Move the windows to the right, omitting tokens
    at the beginning of the text.

    strategy="center": Move the windows to the center, omitting tokens
    at the beginning and the end of the text.

    strategy="spread": Spread out the windows, omitting tokens between
    the windows.

    """
    strategies = set("left right center spread".split())
    assert strategy in strategies
    text_length = len(tokens)
    assert window_size <= text_length
    n_windows, rest = divmod(text_length, window_size)
    if n_windows < 5:
        warnings.warn(f"Less than five windows for text length {text_length} and window size {window_size}. Results might be unreliable. You might want to decrease the window size.")
    for i in range(n_windows):
        if strategy == "left":
            skip = 0
        elif strategy == "right":
            skip = rest
        elif strategy == "center":
            skip = rest // 2
        elif strategy == "spread":
            if n_windows > 1:
                skip = (i * rest) // (n_windows - 1)
            else:
                skip = rest // 2
        yield Text.from_tokens(tokens[skip + i * window_size:(skip + i * window_size) + window_size])


def moving_windows(tokens, window_size, step_size=1):
    """Yield moving windows of text."""
    text_length = len(tokens)
    assert window_size <= text_length
    deque = collections.deque(tokens[0:window_size])
    frequencies = collections.Counter(deque)
    vocabulary_size = len(frequencies)
    frequency_spectrum = collections.Counter(frequencies.values())
    yield Text(list(deque), window_size, vocabulary_size, dict(frequency_spectrum))
    for i in range(window_size, text_length - step_size + 1, step_size):
        for j in range(step_size):
            new = tokens[i + j]
            deque.append(new)
            old = deque.popleft()
            if new != old:
                f_new_0 = frequencies[new]
                f_new_1 = f_new_0 + 1
                f_old_0 = frequencies[old]
                f_old_1 = f_old_0 - 1
                frequencies[new] += 1
                frequencies[old] -= 1
                if frequencies[old] == 0:
                    del frequencies[old]
                if f_new_0 != 0:
                    frequency_spectrum[f_new_0] -= 1
                    if frequency_spectrum[f_new_0] == 0:
                        del frequency_spectrum[f_new_0]
                frequency_spectrum[f_new_1] += 1
                frequency_spectrum[f_old_0] -= 1
                if frequency_spectrum[f_old_0] == 0:
                    del frequency_spectrum[f_old_0]
                if f_old_1 != 0:
                    frequency_spectrum[f_old_1] += 1
                vocabulary_size = len(frequencies)
        yield Text(list(deque), window_size, vocabulary_size, dict(frequency_spectrum))
