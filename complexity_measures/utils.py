#!/usr/bin/env python3

import collections
import logging

import networkx
from nltk.tree import ParentedTree


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
