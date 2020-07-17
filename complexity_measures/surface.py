#!/usr/bin/env python3

import collections
import math
import operator
import statistics

import numpy as np
import scipy.optimize
import scipy.stats

from complexity_measures import utils


# ------------------------------------------------- #
# MEASURES THAT USE SAMPLE SIZE AND VOCABULARY SIZE #
# ------------------------------------------------- #

def type_token_ratio(text):
    """"""
    return text.vocabulary_size / text.text_length


def guiraud_r(text):
    """Guiraud (1954)

    Guiraud, Pierre (1954). Les caractères statistiques du
    vocabulaire: essai de méthodologie. Paris: Presses universitaires
    de France.

    """
    return text.vocabulary_size / math.sqrt(text.text_length)


def herdan_c(text):
    """Herdan (1960, 1964)

    Herdan, Gustav (1960). Type-token mathematics: A textbook of
    mathematical linguistics. Den Haag: Mouton.

    Herdan, Gustav (1964). Quantitative linguistics. London:
    Butterworths.

    """
    return math.log(text.vocabulary_size) / math.log(text.text_length)


def dugast_k(text):
    """Dugast (1979)

    Dugast, Daniel (1979). Vocabulaire et stylistique. 1. Théâtre et
    dialogue. (= Travaux de linguistique quantitative 8). Genève:
    Slatkine.

    """
    return math.log(text.vocabulary_size) / math.log(math.log(text.text_length))


def maas_a2(text):
    """Maas (1972)

    Maas, Heinz-Dieter (1972). “Über den Zusammenhang zwischen
    Wortschatzumfang und Länge eines Textes”. In: Zeitschrift für
    Literaturwissenschaft und Linguistik 2 (8), pp. 73–96.

    """
    return (math.log(text.text_length) - math.log(text.vocabulary_size)) / (math.log(text.text_length) ** 2)


def dugast_u(text):
    """Dugast (1978, 1979). Note that Dugast's U is not defined when
    text_length == vocabulary_size. The function will return NaN in
    this case.

    Dugast, Daniel (1978). “Sur quoi se fonde la notion d’étendue
    théorique du vocabulaire?” In: Le français moderne 46 (1), pp.
    25–32

    Dugast, Daniel (1979). Vocabulaire et stylistique. 1. Théâtre et
    dialogue. (= Travaux de linguistique quantitative 8). Genève:
    Slatkine.

    """
    # as suggested by Andreas, we decrease the vocabulary size by 1,
    # if we only have hapaxes
    # if text_length == vocabulary_size:
    #     vocabulary_size -= 1
    if text.text_length == text.vocabulary_size:
        return math.nan
    return (math.log(text.text_length) ** 2) / (math.log(text.text_length) - math.log(text.vocabulary_size))


def tuldava_ln(text):
    """Tuldava (1977)

    Tuldava, Juhan (1977). “Quantitative relations between the size of
    text and the size of vocabulary”. In: SMIL Quarterly: Journal of
    Linguistic Calculus 4, pp. 28–35

    """
    return (1 - (text.vocabulary_size ** 2)) / ((text.vocabulary_size ** 2) * math.log(text.text_length))


def brunet_w(text, *, a=-0.172):
    """Brunet (1978)

    Brunet, Étienne (1978). Le vocabulaire de Jean Giraudoux.
    Structure et évolution. Statistique et informatique appliquées à
    l’étude des textes à partir des données du Trésor de la Langue
    Française. (= Le Vocabulaire des grands écrivains français 1).
    Genève: Slatkine.

    """
    return text.text_length ** (text.vocabulary_size ** -a)  # Check


def cttr(text):
    """Corrected Type-Token Ration (Carroll, 1964)

    Carroll, John Bissell (1964). Language and Thought. Englewood
    Cliffs, NJ: Prentice-Hall

    """
    return text.vocabulary_size / math.sqrt(2 * text.text_length)


def summer_s(text):
    """Summer's S index"""
    return math.log(math.log(text.vocabulary_size)) / math.log(math.log(text.text_length))


# ------------------------------------------------ #
# MEASURES THAT USE PART OF THE FREQUENCY SPECTRUM #
# ------------------------------------------------ #

def sichel_s(text):
    """Sichel (1975)

    Sichel, Herbert (1975). “On a Distribution Law for Word
    Frequencies”. In: Journal of the American Statistical Association
    70 (351a), pp. 542–547.
    https://doi.org/10.1080/01621459.1975.10482469.

    """
    return text.frequency_spectrum.get(2, 0) / text.vocabulary_size


def michea_m(text):
    """Michéa (1969, 1971). Note that Michéa's M is not defined when there
    are no types with frequency 2. The function will return NaN in
    this case.

    Michéa, René (1969). “Répétition et variété dans l’emploi des
    mots”. In: Bulletin de la société de linguistique de Paris, pp.
    1–24.

    Michéa, René (1971). “De la relation entre le nombre des mots
    d’une fréquence déterminée et celui des mots différents employés
    dans le texte”. In: Cahiers de Lexicologie18 (1), pp. 65–78.
    https://doi.org/10.15122/isbn.978-2-8124-4271-1.p.0067

    """
    try:
        return text.vocabulary_size / text.frequency_spectrum.get(2, 0)
    except ZeroDivisionError:
        return math.nan


def honore_h(text):
    """Honoré (1979). Note that Honoré's H is not defined when there are
    only types with frequency 1. The function will return NaN in this
    case.

    Honoré, Anthony (1979). “Some Simple Measures of Richness of
    Vocabulary”. In: Association for Literary and Linguistic Computing
    Bulletin 7 (2), pp. 172–177.

    """
    # Similar to dugast_u, we decrease the number of hapax legomena by
    # 1, if we only have hapaxes
    hapaxes = text.frequency_spectrum.get(1, 0)
    try:
        return 100 * (math.log(text.text_length) / (1 - (hapaxes / text.vocabulary_size)))
    except ZeroDivisionError:
        return math.nan


# ---------------------------------------------- #
# MEASURES THAT USE THE WHOLE FREQUENCY SPECTRUM #
# ---------------------------------------------- #

def entropy(text):
    """"""
    return sum((freq_size * (-math.log2(freq / text.text_length)) * (freq / text.text_length) for freq, freq_size in text.frequency_spectrum.items()))


def evenness(text):
    """Evenness (https://en.wikipedia.org/wiki/Species_evenness) is also
    known as efficiency or normalized entropy
    (https://en.wikipedia.org/wiki/Entropy_(information_theory))

    """
    return entropy(text) / math.log2(text.vocabulary_size)


def yule_k(text):
    """Yule (1944)

    Yule, George Udny (1944). The Statistical Study of Literary
    Vocabulary. Cambridge: Cambridge University Press.

    """
    return 10000 * (sum((freq_size * (freq / text.text_length) ** 2 for freq, freq_size in text.frequency_spectrum.items())) - (1 / text.text_length))


def simpson_d(text):
    """Simpson (1949)

    Simpson, Edward Hugh (1949). “Measurement of Diversity”. In:
    Nature 163 (4148), p. 688. https://doi.org/10.1038/163688a0.

    """
    return sum((freq_size * (freq / text.text_length) * ((freq - 1) / (text.text_length - 1)) for freq, freq_size in text.frequency_spectrum.items()))


def herdan_vm(text):
    """Herdan (1955)

    Herdan, Gustav (1955). “A new derivation and interpretation of
    Yule’s ’Characteristic’ K”. In: Zeitschrift für angewandte
    Mathematik und Physik 6 (4), pp. 332–339.
    https://doi.org/10.1007/BF01587632.

    """
    return math.sqrt(sum((freq_size * (freq / text.text_length) ** 2 for freq, freq_size in text.frequency_spectrum.items())) - (1 / text.vocabulary_size))


def hdd(text, sample_size=42):
    """McCarthy and Jarvis (2010)

    McCarthy, Philip M. and Scott Jarvis (2010). “MTLD, vocd-D, and
    HD-D: A validation study of sophisticated approaches to lexical
    diversity assessment”. In: Behavior Research Methods 42 (2), pp.
    381–392. https://doi.org/10.3758/BRM.42.2.381.

    """
    # return sum(((1 - scipy.stats.hypergeom.pmf(0, text.text_length, freq_size, sample_size)) / sample_size for freq, freq_size in text.frequency_spectrum.items()))
    return sum(((1 - utils.hypergeom_pmf(0, text.text_length, freq_size, sample_size)) / sample_size for freq, freq_size in text.frequency_spectrum.items()))


# -------------------------------- #
# MEASURES THAT USE THE WHOLE TEXT #
# -------------------------------- #

def mattr(text, window_size=1000):
    """Moving-average type-token ratio (Covington and
    McFall, 2010).

    M.A. Covington, J.D. McFall: Cutting the Gordon Knot. In: Journal
    of Quantitative Linguistics 17,2 (2010), p. 94-100. DOI:
    10.1080/09296171003643098

    """
    ttr_values = []
    window_frequencies = collections.Counter(text.tokens[0:window_size])
    for window_start in range(1, text.text_length - window_size + 1):
        window_end = window_start + window_size
        word_to_pop = text.tokens[window_start - 1]
        word_to_push = text.tokens[window_end - 1]
        window_frequencies[word_to_pop] -= 1
        window_frequencies[word_to_push] += 1
        if window_frequencies[word_to_pop] == 0:
            del window_frequencies[word_to_pop]
        # type-token ratio for the current window:
        ttr_values.append(len(window_frequencies) / window_size)
    return statistics.mean(ttr_values)


def mtld(text, factor_size=0.72):
    """Implementation following the description in McCarthy and Jarvis
    (2010).

    """
    def _mtld(tokens, factor_size, reverse=False):
        factors = 0
        # factor_lengths = []
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
                # factor_lengths.append(token_count)
                types = set()
                token_count = 0
        if token_count > 0:
            ttr = len(types) / token_count
            factors += (1 - ttr) / (1 - factor_size)
            # factor_lengths.append(token_count)
        return len(tokens) / factors
    forward_mtld = _mtld(text.tokens, factor_size)
    reverse_mtld = _mtld(text.tokens, factor_size, reverse=True)
    return statistics.mean((forward_mtld, reverse_mtld))


def average_token_length(text):
    """Average token length in characters."""
    return statistics.mean((len(t) for t in text.tokens))


def _gries_dp(text, n_parts):
    part_size = text.text_length // n_parts
    s_percentage_of_part = 1 / n_parts
    frequencies = np.zeros((text.vocabulary_size, n_parts))
    word_idx = {t: i for i, t in enumerate(sorted(set(text.tokens)))}
    for i in range(n_parts):
        part = text.tokens[i * part_size:(i * part_size) + part_size]
        for token, freq in collections.Counter(part).items():
            frequencies[word_idx[token], i] = freq
    # dp_scores = {token: sum([abs(v[token] / frequency - s_percentage_of_part) for v in v_frequency_corpus_part]) / 2 for token, frequency in f_overall_frequency.items()}
    dp_scores = np.sum(np.absolute(np.subtract(np.divide(frequencies, np.sum(frequencies, axis=1).reshape(-1, 1)), s_percentage_of_part)), axis=1)
    return dp_scores


def gries_dp(text, n_parts):
    """DP (Gries, 2008) has been prosed as a dispersion measure. We use it
    to measure the dispersion of all types and return the average.

    Gries, Stefan Th. (2008). Dispersions and adjusted frequencies in
    corpora. International Journal of Corpus Linguistics 13(4).
    403-437.

    """
    dp_scores = _gries_dp(text, n_parts)
    # return statistics.mean(dp_scores.values())
    return np.mean(dp_scores)


def gries_dp_norm(text, n_parts):
    """DP_norm (Gries, 2008; Lijffijt and Gries, 2012) has been prosed as
    a dispersion measure. We use it to measure the dispersion of all
    types and return the average.

    Gries, Stefan Th. (2008). Dispersions and adjusted frequencies in
    corpora. International Journal of Corpus Linguistics 13(4).
    403-437.

    Lijffijt, Jefrey, Stefan Th. Gries (2012). Correction to
    "Dispersions and adjusted frequencies in corpora". International
    Journal of Corpus Linguistics 17(1). 147-149.

    """
    dp_scores = _gries_dp(text, n_parts)
    # dp_norm_scores = {token: score / (1 - (1 / n_parts)) for token, score in dp_scores.items()}
    # return statistics.mean(dp_norm_scores.values())
    dp_norm_scores = np.divide(dp_scores, (1 - (1 / n_parts)))
    return np.mean(dp_norm_scores)


def kl_divergence(text, n_parts):
    """The Kullback-Leibler divergence has been proposed as a measure of
    dispersion (Gries, to appear). We use it to measure the dispersion
    of all types and return the average.

    Gries, Stefan Th. Analyzing dispersion. In Magali Paquot & Stefan
    Th. Gries (eds.). A practical handbook of corpus linguistics.
    Berlin & New York: Springer.
    http://www.stgries.info/research/ToApp_STG_Dispersion_PHCL.pdf

    """
    part_size = text.text_length // n_parts
    frequencies = np.zeros((text.vocabulary_size, n_parts))
    word_idx = {t: i for i, t in enumerate(sorted(set(text.tokens)))}
    for i in range(n_parts):
        part = text.tokens[i * part_size:(i * part_size) + part_size]
        for token, freq in collections.Counter(part).items():
            frequencies[word_idx[token], i] = freq
    # kld_scores = {token: sum([0 if v[token] == 0 else (v[token] / frequency) * math.log2((v[token] / frequency) * n_parts) for v in v_frequency_corpus_part]) for token, frequency in f_overall_frequency.items()}
    relative_frequencies = np.divide(frequencies, np.sum(frequencies, axis=1).reshape(-1, 1))
    with np.errstate(divide='ignore'):
        log = np.log2(np.multiply(relative_frequencies, n_parts))
    log[np.isneginf(log)] = 0
    kld_scores = np.sum(np.multiply(relative_frequencies, log), axis=1)
    return np.mean(kld_scores)


# ---------------------------------- #
# PARAMETERS OF PROBABILISTIC MODELS #
# ---------------------------------- #

def orlov_z(text, max_iterations=100, tolerance=1):
    """Orlov (1983)"""
    def f(z, text_length, vocabulary_size, p_star):
        if z <= 0:
            return math.nan
        return (z / math.log(p_star * z)) * (text_length / (text_length - z)) * math.log(text_length / z) - vocabulary_size

    # def fprime(z, text_length, vocabulary_size, p_star):
    #     """Derivative obtained from WolframAlpha:
    #     https://www.wolframalpha.com/input/?x=0&y=0&i=(x+%2F+(log(p+*+x)))+*+(n+%2F+(n+-+x))+*+log(n+%2F+x)+-+v

    #     """
    #     if z <= 0:
    #         return math.nan
    #     return (text_length * ((z - text_length) * math.log(p_star * z) + math.log(text_length / z) * (text_length * math.log(p_star * z) - text_length + z))) / (((text_length - z) ** 2) * (math.log(p_star * z) ** 2))

    # def fprime2(z, text_length, vocabulary_size, p_star):
    #     """Derivative obtained from WolframAlpha:
    #     https://www.wolframalpha.com/input/?i=%28n+%28%28x+-+n%29+log%28p+x%29+%2B+log%28n%2Fx%29+%28n+log%28p+x%29+-+n+%2B+x%29%29%29%2F%28%28n+-+x%29%5E2+log%5E2%28p+x%29%29

    #     """
    #     if z <= 0:
    #         return math.nan
    #     return -(text_length * (math.log(text_length / z) * ((text_length ** 2 - z ** 2) * math.log(p_star * z) - 2 * text_length * z * math.log(p_star * z) ** 2 - 2 * (text_length - z) ** 2) + (text_length - z) * math.log(p_star * z) * ((text_length + z) * math.log(p_star * z) - 2 * text_length + 2 * z)))/(z * (text_length - z) ** 3 * math.log(p_star * z) ** 3)

    most_frequent = max(text.frequency_spectrum.keys())
    p_star = most_frequent / text.text_length
    # try values between 10 and 1,000,000,000:
    values = [(10 ** i + 0.1, f(10 ** i + 0.1, text.text_length, text.vocabulary_size, p_star)) for i in range(1, 10)]
    try:
        z_min = max([t for t in values if t[1] < 0], key=operator.itemgetter(1))[0]
        z_max = min([t for t in values if t[1] > 0 and t[0] > z_min], key=operator.itemgetter(1))[0]
    except ValueError:
        return math.nan
    sol_toms748 = scipy.optimize.root_scalar(f, args=(text.text_length, text.vocabulary_size, p_star), method="toms748", bracket=(z_min, z_max), xtol=tolerance, maxiter=max_iterations)
    # sol_halley = scipy.optimize.root_scalar(f, args=(text.text_length, text.vocabulary_size, p_star), method="halley", fprime=fprime, fprime2=fprime2, x0=z_max / 2, xtol=tolerance, maxiter=max_iterations)
    return sol_toms748.root


# --------------------- #
# CONVENIENCE FUNCTIONS #
# --------------------- #

def sttr(tokens, window_size=1000, strategy="spread"):
    """Standardized type-token ratio (Kubát and Milička, 2013; Evert et
    al., 2017)

    Kubát, Miroslav, Jiří Milička (2013). Vocabulary richness measure
    in genres. In: Journal of Quantitative Linguistics 20 (4), pp.
    339–349

    Evert, Stefan, Sebastian Wankerl, Elmar Nöth (2017). Reliable
    measures of syntactic and lexical complexity: The case of Iris
    Murdoch. In: Proceedings of the Corpus Linguistics 2017
    Conference, Birmingham, UK.
    http://purl.org/stefan.evert/PUB/EvertWankerlNoeth2017.pdf

    """
    return bootstrap(type_token_ratio, tokens, window_size, strategy)


# ------------- #
# BOOTSTRAPPING #
# ------------- #

def bootstrap(measure, tokens, window_size, strategy="spread", **kwargs):
    """Calculate bootstrap for surface-based measures as explained in
    Evert et al. (2017).

    kwargs are passed to measure

    Evert, Stefan, Sebastian Wankerl, Elmar Nöth (2017). Reliable
    measures of syntactic and lexical complexity: The case of Iris
    Murdoch. In: Proceedings of the Corpus Linguistics 2017
    Conference, Birmingham, UK.
    http://purl.org/stefan.evert/PUB/EvertWankerlNoeth2017.pdf

    """
    results = []
    for window in utils.disjoint_windows(tokens, window_size, strategy):
        results.append(measure(window, **kwargs))
    return statistics.mean(results), utils.confidence_interval(results), results
