#!/usr/bin/env python3

import collections
import math
import statistics
import warnings


# ------------------------------------------------- #
# MEASURES THAT USE SAMPLE SIZE AND VOCABULARY SIZE #
# ------------------------------------------------- #

def type_token_ratio(sample_size, vocabulary_size):
    """"""
    return vocabulary_size / sample_size


def guiraud_r(sample_size, vocabulary_size):
    """Guiraud (1954)"""
    return vocabulary_size / math.sqrt(sample_size)


def herdan_c(sample_size, vocabulary_size):
    """Herdan (1960, 1964)"""
    return math.log(vocabulary_size) / math.log(sample_size)


def dugast_k(sample_size, vocabulary_size):
    """Dugast (1979)"""
    return math.log(vocabulary_size) / math.log(math.log(sample_size))


def maas_a2(sample_size, vocabulary_size):
    """Maas (1972)"""
    return (math.log(sample_size) - math.log(vocabulary_size)) / (math.log(sample_size) ** 2)


def dugast_u(sample_size, vocabulary_size):
    """Dugast (1978, 1979)"""
    return (math.log(sample_size) ** 2) / (math.log(sample_size) - math.log(vocabulary_size))


def tuldava_ln(sample_size, vocabulary_size):
    """Tuldava (1977)"""
    return (1 - (vocabulary_size ** 2)) / ((vocabulary_size ** 2) * math.log(sample_size))


def brunet_w(sample_size, vocabulary_size):
    """Brunet (1978)"""
    a = -0.172
    return sample_size ** (vocabulary_size ** -a)  # Check


# ------------------------------------------------ #
# MEASURES THAT USE PART OF THE FREQUENCY SPECTRUM #
# ------------------------------------------------ #

def sichel_s(vocabulary_size, frequency_spectrum):
    """Sichel (1975)"""
    return frequency_spectrum[2] / vocabulary_size


def michea_m(vocabulary_size, frequency_spectrum):
    """Michéa (1969, 1971)"""
    return vocabulary_size / frequency_spectrum[2]


def honore_h(sample_size, vocabulary_size, frequency_spectrum):
    """Honoré (1979)"""
    return 100 * (math.log(sample_size) / (1 - ((frequency_spectrum[1]) / (vocabulary_size))))


# ---------------------------------------------- #
# MEASURES THAT USE THE WHOLE FREQUENCY SPECTRUM #
# ---------------------------------------------- #

def entropy(sample_size, frequency_spectrum):
    """"""
    return sum((freq_size * (- math.log(freq / sample_size)) * (freq / sample_size) for freq, freq_size in frequency_spectrum.items()))


def yule_k(sample_size, frequency_spectrum):
    """Yule (1944)"""
    return 10000 * ((sum((freq_size * (freq / sample_size) ** 2 for freq, freq_size in frequency_spectrum.items())) - sample_size) / (sample_size ** 2))


def simpson_d(sample_size, frequency_spectrum):
    """"""
    return sum((freq_size * (freq / sample_size) * ((freq - 1) / (sample_size - 1)) for freq, freq_size in frequency_spectrum.items()))


def herdan_vm(sample_size, vocabulary_size, frequency_spectrum):
    """Herdan (1955)"""
    return math.sqrt(sum((freq_size * (freq / sample_size) ** 2 for freq, freq_size in frequency_spectrum.items())) - (1 / vocabulary_size))


# ---------------------------------- #
# PARAMETERS OF PROBABILISTIC MODELS #
# ---------------------------------- #

def orlov_z(sample_size, vocabulary_size, frequency_spectrum, max_iterations=100, min_tolerance=1):
    """Orlov (1983)"""
    most_frequent = max(frequency_spectrum.keys())
    p_star = most_frequent / sample_size
    lower_z, upper_z = None, None
    z = int(sample_size / 100)  # our initial guess
    for i in range(max_iterations):
        estimated_vocabulary_size = (z / math.log(p_star * z)) * (sample_size / (sample_size - z)) * math.log(sample_size / z)
        if abs(vocabulary_size - estimated_vocabulary_size) <= min_tolerance:
            print(i, z)
            break
        if estimated_vocabulary_size < vocabulary_size:
            lower_z = z
            if upper_z is not None:
                z = int((z + upper_z) / 2)
            else:
                z *= 2
        else:
            upper_z = z
            if lower_z is not None:
                z = int((z + lower_z) / 2)
            else:
                z = int(z / 2)
    else:
        warnings.warn("Exceeded max_iterations")
    return z


# -------------------------------- #
# MEASURES THAT USE THE WHOLE TEXT #
# -------------------------------- #

def MATTR_(wordlist, winsize):
    results = []
    word_count = collections.Counter(wordlist[0:winsize])
    for win_start in range(1, len(wordlist)-(winsize+1)):
        win_end = win_start + winsize
        word_count[wordlist[win_start-1]] -= 1
        if word_count[wordlist[win_start-1]] == 0:
            del(word_count[wordlist[win_start-1]])
        word_count[wordlist[win_end]] += 1
        results.append(len(word_count.values())/winsize)  # calculate ttr for the text window
    return results


def MATTR(wordlist, winsize=1000):
    """
    Calculate The Moving-Average Type-Token Ratio
    M.A. Covington,J.D. McFall: Cutting the Gordon Knot. In: Journal of Quantitative
    Linguistics 17,2 (2010), p. 94-100.
    DOI: 10.1080/09296171003643098

    >>> a = np.array(50*['a'] + 50*['b'])
    >>> b = np.array(10*['a'] + 10*['b'] + 10*['c'] + 10*['d'] + 10*['e'] + 10*['f'] \
                     + 10*['g'] + 10*['h'] + 10*['i'] + 10*['j'])
    >>> np.random.seed(3)
    >>> np.random.shuffle(a)
    >>> np.random.shuffle(b)
    >>> MATTR(a, 10)
    0.2
    >>> MATTR(b, 10)
    0.6875
    """
    return statistics.mean(MATTR_(wordlist, winsize))
