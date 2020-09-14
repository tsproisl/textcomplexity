#!/usr/bin/env python3

import collections
import functools
import logging
import math
import statistics
import unicodedata
import warnings

import networkx
from nltk.tree import ParentedTree
import numpy
import scipy.special

from complexity_measures.text import Text


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
        warnings.warn("Less than five windows for text length %d and window size %d. Results might be unreliable. You might want to decrease the window size.")
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


def confidence_interval(results):
    return 1.96 * statistics.stdev(results) / math.sqrt(len(results))


@functools.lru_cache(maxsize=1024)
def betaln(a, b):
    return scipy.special.betaln(a, b)


@functools.lru_cache(maxsize=1024)
def hypergeom_pmf(k, M, n, N):
    tot, good = M, n
    bad = tot - good
    result = (betaln(good+1, 1) + betaln(bad+1, 1) + betaln(tot-N+1, N+1) -
              betaln(k+1, good-k+1) - betaln(N-k+1, bad-N+k+1) -
              betaln(tot+1, 1))
    return numpy.exp(result)


def read_jtf_sentences(f):
    """Read a file in jtf format, i.e. a tab-separated file with 15
    columns.

    """
    header = f.readline().rstrip().split("\t")
    assert header == "SectionId ParagraphId SentenceId TokenId Begin End Token Lemma CPOS POS Morphology DependencyHead DependencyRelation NamedEntity CorefId".split()
    sentence_id = None
    sentence = []
    for line in f:
        fields = line.rstrip().split("\t")
        if fields[2] != sentence_id:
            if sentence_id is not None:
                yield sentence
                sentence = []
            sentence_id = fields[2]
        sentence.append(fields)
    yield sentence


def read_jtf_graphs(f):
    """Read a file in jtf format, i.e. a tab-separated file with 15
    columns, and convert the sentences to networkx graphs.

    """
    def attributes(t):
        return int(t[3]), {"token": t[6], "lemma": t[7], "cpos": t[8], "pos": t[9], "morphology": t[10]}
    sentences = read_jtf_sentences(f)
    for sentence in sentences:
        sentence_id = sentence[0][2]
        g = networkx.DiGraph(sentence_id=sentence_id)
        g.add_nodes_from([attributes(t) for t in sentence])
        token_to_id = collections.defaultdict(list)
        for token in sentence:
            token_to_id[token[6]].append(int(token[3]))
        for token in sentence:
            tid = int(token[3])
            if token[11] == "ROOT":
                g.node[tid]["root"] = "root"
            else:
                candidates = [x for x in token_to_id[token[11]] if x != tid]
                governor = candidates[0]
                if len(candidates) > 1:
                    governor = min(candidates, key=lambda x: abs(x - tid))
                g.add_edge(governor, tid, relation=token[12])
        sensible, explanation = is_sensible_graph(g)
        if sensible:
            yield g
        else:
            logging.warn("%s. Ignoring sentence with ID %s." % (explanation, sentence_id))


def read_txt_csv_sentences(f):
    """Read a file in txt.csv format, i.e. a tab-separated file with 21
    columns.

    """
    header = f.readline().rstrip().split("\t")
    assert header == "SectionId ParagraphId SentenceId TokenId Begin End Token Lemma CPOS POS Chunk Morphology Hyphenation DependencyHead DependencyRelation NamedEntity QuoteMarker CoreferenceChainIds SyntaxTree Predicate SemanticArgumentIndex".split()
    sentence_id = None
    sentence = []
    for line in f:
        fields = line.rstrip().split("\t")
        if fields[2] != sentence_id:
            if sentence_id is not None:
                yield sentence
                sentence = []
            sentence_id = fields[2]
        sentence.append(fields)
    yield sentence


def read_txt_csv_graphs(f, warnings=True):
    """Read a file in txt.csv format, i.e. a tab-separated file with 21
    columns, convert the dependency parses to networkx graphs and the
    phrase structure trees to NLTK ParentedTrees.

    """
    def attributes(t):
        return int(t[3]), {"token": t[6], "lemma": t[7], "cpos": t[8], "pos": t[9], "morphology": t[11]}
    sentences = read_txt_csv_sentences(f)
    for sentence in sentences:
        sentence_id = sentence[0][2]
        g = networkx.DiGraph(sentence_id=sentence_id)
        g.add_nodes_from([attributes(t) for t in sentence])
        tree = []
        for token in sentence:
            tid = int(token[3])
            gov = int(token[13])
            rel = token[14]
            tree_frag = token[18]
            if gov == -1:
                g.node[tid]["root"] = "root"
            else:
                g.add_edge(gov, tid, relation=rel)
            tree_tok = token[6]
            tree_tok = tree_tok.replace("(", "-LRB-")
            tree_tok = tree_tok.replace(")", "-RRB-")
            tree_pos = token[9]
            tree_pos = tree_pos.replace("(", "-LRB-")
            tree_pos = tree_pos.replace(")", "-RRB-")
            tree_frag = tree_frag.replace("*", "(%s %s)" % (tree_pos, tree_tok))
            tree.append(tree_frag)
        tree = "".join(tree)
        sensible, explanation = is_sensible_graph(g)
        if sensible:
            try:
                tree = ParentedTree.fromstring(tree)
            except ValueError:
                if warnings:
                    logging.warn("Failed to construct parse tree. Ignoring sentence with ID %s: %s" % (sentence_id, tree))
            else:
                yield g, tree
        else:
            if warnings:
                logging.warn("%s. Ignoring sentence with ID %s." % (explanation, sentence_id))


def is_sensible_graph(g):
    """Check if g is a sensible syntactic representation of a sentence,
    i.e. rooted, connected, …

    """
    # is there a vertex explicitly labeled as "root"?
    roots = [v for v, l in g.nodes(data=True) if "root" in l]
    if len(roots) == 0:
        return False, "There is no explicit 'root' vertex"
    if len(roots) > 1:
        return False, "There is more than one explicit 'root' vertex"
    # is the graph connected?
    if not networkx.is_weakly_connected(g):
        return False, "The graph is not connected"
    # is the "root" vertex really a root, i.e. is there a path to
    # every other vertex?
    root = roots[0]
    other_vertices = set(g.nodes())
    other_vertices.remove(root)
    if not all([networkx.has_path(g, root, v) for v in other_vertices]):
        return False, "The vertex labeled as 'root' is not actually a root"
    return True, ""


def get_sentences(f):
    """A generator over the sentences in f."""
    sentence = []
    for line in f:
        line = line.strip()
        if line == "":
            yield sentence
            sentence = []
        else:
            sentence.append(line.split("\t"))
    if len(sentence) > 0:
        yield sentence


def read_tsv(f, voc=True, dep=True, const=True, ignore_punct=False, warnings=True):
    """Read a tab-separated file with six columns: word index, word,
    part-of-speech tag, index of dependency head, dependency relation,
    phrase structure tree. There must be an empty line after each
    sentence. Missing values can be replaced with an underscore (_).

    """
    def attributes(t):
        return int(t[0]), {"token": t[1], "pos": t[2]}

    sentences = get_sentences(f)
    for sentence_id, sentence in enumerate(sentences):
        try:
            assert all((len(t) == 6 for t in sentence))
        except AssertionError:
            logging.warn("Malformed sentence (no. %d) does not have six columns: %s" % (sentence_id, repr(sentence)))
            continue
        result = []
        if voc:
            tokens = [t[1] for t in sentence]
            if ignore_punct:
                tokens = [t for t in tokens if not all((unicodedata.category(c)[0] == "P" for c in t))]
            result.append(tokens)
        else:
            result.append(None)
        if dep:
            if any((t[3] == "_" for t in sentence)) or any((t[4] == "_" for t in sentence)):
                result.append(None)
            else:
                g = networkx.DiGraph(sentence_id=sentence_id)
                g.add_nodes_from([attributes(t) for t in sentence])
                for token in sentence:
                    tid = int(token[0])
                    gov = int(token[3])
                    rel = token[4]
                    if gov == -1:
                        g.node[tid]["root"] = "root"
                    else:
                        g.add_edge(gov, tid, relation=rel)
                sensible, explanation = is_sensible_graph(g)
                if not sensible:
                    logging.warn("%s. Ignoring sentence with ID %s." % (explanation, sentence_id))
                    g = None
                result.append(g)
        else:
            result.append(None)
        if const:
            if any((t[5] == "_" for t in sentence)):
                result.append(None)
            else:
                tree = []
                for token in sentence:
                    tree_frag = token[5]
                    tree_tok = token[1]
                    tree_tok = tree_tok.replace("(", "-LRB-")
                    tree_tok = tree_tok.replace(")", "-RRB-")
                    tree_pos = token[2]
                    tree_pos = tree_pos.replace("(", "-LRB-")
                    tree_pos = tree_pos.replace(")", "-RRB-")
                    tree_frag = tree_frag.replace("*", "(%s %s)" % (tree_pos, tree_tok))
                    tree.append(tree_frag)
                tree = "".join(tree)
                try:
                    tree = ParentedTree.fromstring(tree)
                except ValueError:
                    logging.warn("Failed to construct parse tree from sentence %s: %s" % (sentence_id, tree))
                    tree = None
                result.append(tree)
        else:
            result.append(None)
        yield result


def read_conll(f, ignore_punct=False, warnings=True):
    """Read a tab-separated file with seven columns: word index, word,
    lemma, part-of-speech tag, empty field (_), index of dependency
    head, dependency relation. There must be an empty line after each
    sentence. Missing values can be replaced with an underscore (_).

    """
    def attributes(t):
        return int(t[0]), {"token": t[1], "lemma": t[2], "pos": t[3]}

    sentences = get_sentences(f)
    for sentence_id, sentence in enumerate(sentences):
        try:
            assert all((len(t) == 7 for t in sentence))
        except AssertionError:
            logging.warn("Malformed sentence (no. %d) does not have six columns: %s" % (sentence_id, repr(sentence)))
            continue
        result = []
        tokens = [t[1] for t in sentence]
        lemmas = [t[2] for t in sentence]
        pos = [t[3] for t in sentence]
        if ignore_punct:
            punct = [all((unicodedata.category(c)[0] == "P" for c in t)) for t in tokens]
            tokens = [t for t, p in zip(tokens, punct) if not p]
            lemmas = [t for t, p in zip(lemmas, punct) if not p]
            pos = [t for t, p in zip(pos, punct) if not p]
        result.append(tokens)
        result.append(lemmas)
        result.append(pos)
        if any((t[5] == "_" for t in sentence)) or any((t[6] == "_" for t in sentence)):
            result.append(None)
        else:
            g = networkx.DiGraph(sentence_id=sentence_id)
            g.add_nodes_from([attributes(t) for t in sentence])
            for token in sentence:
                tid = int(token[0])
                gov = int(token[5])
                rel = token[6]
                if gov == 0:
                    g.node[tid]["root"] = "root"
                else:
                    g.add_edge(gov, tid, relation=rel)
            sensible, explanation = is_sensible_graph(g)
            if not sensible:
                logging.warn("%s. Ignoring sentence with ID %s." % (explanation, sentence_id))
                g = None
            result.append(g)
        yield result
