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
    """Orlov (1983)

    Approximation via Newton's method.

    """
    def function(text_length, vocabulary_size, p_star, z):
        return (z / math.log(p_star * z)) * (text_length / (text_length - z)) * math.log(text_length / z) - vocabulary_size

    def derivative(text_length, vocabulary_size, p_star, z):
        """Derivative obtained from WolframAlpha:
        https://www.wolframalpha.com/input/?x=0&y=0&i=(x+%2F+(log(p+*+x)))+*+(n+%2F+(n+-+x))+*+log(n+%2F+x)+-+v

        """
        return (text_length * ((z - text_length) * math.log(p_star * z) + math.log(text_length / z) * (text_length * math.log(p_star * z) - text_length + z))) / (((text_length - z) ** 2) * (math.log(p_star * z) ** 2))
    most_frequent = max(frequency_spectrum.keys())
    p_star = most_frequent / text_length
    z = text_length / 2         # our initial guess
    for i in range(max_iterations):
        # print(i, text_length, vocabulary_size, p_star, z)
        next_z = z - (function(text_length, vocabulary_size, p_star, z) / derivative(text_length, vocabulary_size, p_star, z))
        abs_diff = abs(z - next_z)
        z = next_z
        if abs_diff <= min_tolerance:
            break
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
        return len(tokens) / factors
    forward_mtld = _mtld(tokens, factor_size)
    reverse_mtld = _mtld(tokens, factor_size, reverse=True)
    return statistics.mean((forward_mtld, reverse_mtld))


def _sttr_ci(results):
    """calculate the confidence interval for sttr """
    return 1.96 * statistics.stdev(results) / math.sqrt(len(results))


def sttr(tokens, window_size=1000, ci=False):
    """calculate standardized type-token ratio
    originally Kubat&Milicka 2013. Much better explained
    in Evert et al. 2017.
    :param ci:  additionally calculate and return the confidence interval, returns a tuple
    """
    results = []
    for i in range(int(len(tokens) / window_size)):  # ignore last partial chunk
        text_length, vocabulary_size = preprocess(tokens[i * window_size:(i * window_size) + window_size])
        results.append(type_token_ratio(text_length, vocabulary_size))
    if ci:
        return (statistics.mean(results), _sttr_ci(results))
    return statistics.mean(results)


def preprocess(tokens, fs=False):
    """Return text length, vocabulary size and optionally the frequency
    spectrum.

    :param fs: additionally calculate and return the frequency
               spectrum

    """
    text_length = len(tokens)
    vocabulary_size = len(set(tokens))
    if fs:
        frequency_list = collections.Counter(tokens)
        frequency_spectrum = dict(collections.Counter(frequency_list.values()))
        return text_length, vocabulary_size, frequency_spectrum
    return text_length, vocabulary_size


def bootstrap(tokens, measure='type_token_ratio', window_size=1000, ci=False, raw=False):
    """calculate bootstrap for lex diversity measures
    as explained in Evert et al. 2017. if measure='type_token_ratio' it calculates
    standardized type-token ratio
    :param ci:  additionally calculate and return the confidence interval, returns a tuple
    :param raw:  return the raw results
    """
    results = []
    measures = dict(type_token_ratio=type_token_ratio,
                    guiraud_r=guiraud_r, herdan_c=herdan_c,
                    dugast_k=dugast_k, maas_a2=maas_a2,
                    dugast_u=dugast_u, tuldava_ln=tuldava_ln,
                    brunet_w=brunet_w, cttr=cttr, summer_s=summer_s,
                    sichel_s=sichel_s, michea_m=michea_m,
                    honore_h=honore_h, entropy=entropy, yule_k=yule_k,
                    simpson_d=simpson_d, herdan_vm=herdan_vm, hdd=hdd,
                    orlov_z=orlov_z, mtld=mtld)
    # tl_vs: text_length, vocabulary_size
    # vs_fs: vocabulary_size, frequency_spectrum
    # tl_vs_fs: text_length, vocabulary_size, frequency_spectrum
    # tl_fs: text_length, frequency_spectrum
    # t: tokens
    classes = dict(tl_vs=("type_token_ratio", "guiraud_r", "herdan_c",
                          "dugast_k", "maas_a2", "dugast_u",
                          "tuldava_ln", "brunet_w", "cttr",
                          "summer_s"),
                   vs_fs=("sichel_s", "michea_m"),
                   tl_vs_fs=("honore_h", "herdan_vm", "orlov_z"),
                   tl_fs=("entropy", "yule_k", "simpson_d", "hdd"),
                   t=("mtld",))
    measure_to_class = {m: c for c, v in classes.items() for m in v}
    func = measures[measure]
    cls = measure_to_class[measure]
    for i in range(int(len(tokens) / window_size)):  # ignore last partial chunk
        chunk = tokens[i * window_size:(i * window_size) + window_size]
        text_length, vocabulary_size, frequency_spectrum = preprocess(chunk, fs=True)
        if cls == "tl_vs":
            result = func(text_length, vocabulary_size)
        elif cls == "vs_fs":
            result = func(vocabulary_size, frequency_spectrum)
        elif cls == "tl_vs_fs":
            result = func(text_length, vocabulary_size, frequency_spectrum)
        elif cls == "tl_fs":
            result = func(text_length, frequency_spectrum)
        elif cls == "t":
            result = func(chunk)
        results.append(result)
    if raw:
        return results
    if ci:
        return (statistics.mean(results), _sttr_ci(results))
    return statistics.mean(results)
