#!/usr/bin/env python3

import collections
import math
import statistics
import warnings

import scipy.stats


# ------------------------------------------------- #
# MEASURES THAT USE SAMPLE SIZE AND VOCABULARY SIZE #
# ------------------------------------------------- #

def type_token_ratio(text_length, vocabulary_size):
    """"""
    return vocabulary_size / text_length


def guiraud_r(text_length, vocabulary_size):
    """Guiraud (1954)"""
    return vocabulary_size / math.sqrt(text_length)


def herdan_c(text_length, vocabulary_size):
    """Herdan (1960, 1964)"""
    return math.log(vocabulary_size) / math.log(text_length)


def dugast_k(text_length, vocabulary_size):
    """Dugast (1979)"""
    return math.log(vocabulary_size) / math.log(math.log(text_length))


def maas_a2(text_length, vocabulary_size):
    """Maas (1972)"""
    return (math.log(text_length) - math.log(vocabulary_size)) / (math.log(text_length) ** 2)


def dugast_u(text_length, vocabulary_size):
    """Dugast (1978, 1979)"""
    return (math.log(text_length) ** 2) / (math.log(text_length) - math.log(vocabulary_size))


def tuldava_ln(text_length, vocabulary_size):
    """Tuldava (1977)"""
    return (1 - (vocabulary_size ** 2)) / ((vocabulary_size ** 2) * math.log(text_length))


def brunet_w(text_length, vocabulary_size):
    """Brunet (1978)"""
    a = -0.172
    return text_length ** (vocabulary_size ** -a)  # Check


def cttr(text_length, vocabulary_size):
    """Carroll's Corrected Type-Token Ration"""
    return vocabulary_size / math.sqrt(2 * text_length)


def summer_s(text_length, vocabulary_size):
    """Summer's S index"""
    return math.log(math.log(vocabulary_size)) / math.log(math.log(text_length))


# ------------------------------------------------ #
# MEASURES THAT USE PART OF THE FREQUENCY SPECTRUM #
# ------------------------------------------------ #

def sichel_s(vocabulary_size, frequency_spectrum):
    """Sichel (1975)"""
    return frequency_spectrum[2] / vocabulary_size


def michea_m(vocabulary_size, frequency_spectrum):
    """Michéa (1969, 1971)"""
    return vocabulary_size / frequency_spectrum[2]


def honore_h(text_length, vocabulary_size, frequency_spectrum):
    """Honoré (1979)"""
    return 100 * (math.log(text_length) / (1 - ((frequency_spectrum[1]) / (vocabulary_size))))


# ---------------------------------------------- #
# MEASURES THAT USE THE WHOLE FREQUENCY SPECTRUM #
# ---------------------------------------------- #

def entropy(text_length, frequency_spectrum):
    """"""
    return sum((freq_size * (- math.log(freq / text_length)) * (freq / text_length) for freq, freq_size in frequency_spectrum.items()))


def yule_k(text_length, frequency_spectrum):
    """Yule (1944)"""
    return 10000 * (sum((freq_size * (freq / text_length) ** 2 for freq, freq_size in frequency_spectrum.items())) - (1 / text_length))


def simpson_d(text_length, frequency_spectrum):
    """"""
    return sum((freq_size * (freq / text_length) * ((freq - 1) / (text_length - 1)) for freq, freq_size in frequency_spectrum.items()))


def herdan_vm(text_length, vocabulary_size, frequency_spectrum):
    """Herdan (1955)"""
    return math.sqrt(sum((freq_size * (freq / text_length) ** 2 for freq, freq_size in frequency_spectrum.items())) - (1 / vocabulary_size))


def hdd(text_length, frequency_spectrum, sample_size=42):
    """McCarthy and Jarvis (2010)"""
    return sum(((1 - scipy.stats.hypergeom.pmf(0, text_length, freq, sample_size)) / sample_size for word, freq in frequency_spectrum.items()))


# ---------------------------------- #
# PARAMETERS OF PROBABILISTIC MODELS #
# ---------------------------------- #

def orlov_z(text_length, vocabulary_size, frequency_spectrum, max_iterations=100, min_tolerance=1):
    """Orlov (1983)"""
    most_frequent = max(frequency_spectrum.keys())
    p_star = most_frequent / text_length
    lower_z, upper_z = None, None
    z = int(text_length / 100)  # our initial guess
    for i in range(max_iterations):
        estimated_vocabulary_size = (z / math.log(p_star * z)) * (text_length / (text_length - z)) * math.log(text_length / z)
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

def mattr(tokens, window_size=1000):
    """Calculate the Moving-Average Type-Token Ratio (Covington and
    McFall, 2010).

    M.A. Covington, J.D. McFall: Cutting the Gordon Knot. In: Journal
    of Quantitative Linguistics 17,2 (2010), p. 94-100. DOI:
    10.1080/09296171003643098

    """
    ttr_values = []
    window_frequencies = collections.Counter(tokens[0:window_size])
    for window_start in range(1, len(tokens) - (window_size + 1)):
        window_end = window_start + window_size
        word_to_pop = tokens[window_start - 1]
        window_frequencies[word_to_pop] -= 1
        window_frequencies[tokens[window_end]] += 1
        if window_frequencies[word_to_pop] == 0:
            del window_frequencies[word_to_pop]
        # type-token ratio for the current window:
        ttr_values.append(len(window_frequencies) / window_size)
    return statistics.mean(ttr_values)


def mtld(tokens, factor_size=0.72):
    """Implementation following the description in McCarthy and Jarvis
    (2010).

    """
    def _mtld(tokens, factor_size, reverse=False):
        factors = 0
        factor_lengths = []
        types = set()
        token_count = 0
        token_iterator = iter(tokens)
        if reverse:
            token_iterator = reversed(tokens)
        for token in token_iterator:
            types.add(token)
            token_count += 1
            if len(types) / token_count <= factor_size:
                factors += 1
                factor_lengths.append(token_count)
                types = set()
                token_count = 0
        if token_count > 0:
            ttr = len(types) / token_count
            factors += (1 - ttr) / (1 - factor_size)
            factor_lengths.append(token_count)
        return len(tokens) / sum(factors)
    forward_mtld = _mtld(tokens, factor_size)
    reverse_mtld = _mtld(tokens, factor_size, reverse=True)
    return statistics.mean((forward_mtld, reverse_mtld))


def sttr_ci(results):
    """calculate the confidence interval for sttr """
    return 1.96 * statistics.stdev(results) / math.sqrt(len(results))


def sttr(tokens, winsize=1000, ci=False):
    """calculate standardized type-token ratio
    originally Kubat&Milicka 2013. Much better explained
    in Evert et al. 2017.
    :param ci:  additionally calculate and return the confidence interval, returns a tuple
    """
    results = []
    for i in range(int(len(tokens) / winsize)):  # ignore last partial chunk
        text_length, vocabulary_size = preprocess(tokens[i * winsize:(i * winsize) + winsize])
        results.append(type_token_ratio(text_length, vocabulary_size))
    if not ci:
        return statistics.mean(results)
    else:
        return (statistics.mean(results), sttr_ci(results))


def preprocess(tokens):
    """TODO: add option to calculate frequence spectrum"""
    return len(tokens), len(set(tokens))


def bootstrap(tokens, metric='type_token_ratio', winsize=1000, ci=False):
    """calculate bootstrap for lex diversity measures
    as explained in Evert et al. 2017. if metric='type_token_ratio' it calculates
    standardized type-token ratio
    :param ci:  additionally calculate and return the confidence interval, returns a tuple
    """
    results = []
    metrics = dict(type_token_ratio=type_token_ratio,
                   guiraud_r=guiraud_r, herdan_c=herdan_c,
                   dugast_k=dugast_k, maas_a2=maas_a2,
                   dugast_u=dugast_u, tuldava_ln=tuldava_ln,
                   brunet_w=brunet_w, cttr=cttr, summer_s=summer_s)
    func = metrics[metric]
    for i in range(int(len(tokens) / winsize)):  # ignore last partial chunk
        text_length, vocabulary_size = preprocess(tokens[i * winsize:(i * winsize) + winsize])
        results.append(func(text_length, vocabulary_size))
    if not ci:
        return statistics.mean(results)
    else:
        return (statistics.mean(results), sttr_ci(results))
