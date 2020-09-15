#!/usr/bin/env python3

import collections
import logging

import networkx
from nltk.tree import ParentedTree

from complexity_measures.utils import graph

TsvToken = collections.namedtuple("TsvToken", "id word pos head deprel pstree".split())
Token = collections.namedtuple("Token", "word pos".split())


def read_tsv_sentences(f, *, ignore_punct=False, punct_tags=None, warnings=True):
    """Read a tab-separated file with six columns: word index, word,
    part-of-speech tag, index of dependency head, dependency relation,
    phrase structure tree. There must be an empty line after each
    sentence. Missing values can be replaced with an underscore (_).

    """
    def attributes(t):
        return {"word": t.word, "pos": t.pos}

    for sent_id, sentence in enumerate(_get_sentences(f)):
        tokens = [t for t in sentence]
        if ignore_punct:
            tokens = [t for t in tokens if t.pos not in punct_tags]
        forms = [t.word for t in tokens]
        tokens = [Token(t.word, t.pos) for t in tokens]
        if all((t.head != "_" for t in sentence)) and all((t.deprel != "_" for t in sentence)):
            g = networkx.DiGraph(sentence_id=sent_id)
            g.add_nodes_from([(i, attributes(t)) for i, t in enumerate(sentence)])
            id_to_enumeration = {t.id: i for i, t in enumerate(sentence)}
            for i, token in enumerate(sentence):
                if token.head == "-1":
                    g.node[i]["root"] = "root"
                else:
                    g.add_edge(id_to_enumeration[token.head], i, relation=token.deprel)
            sensible, explanation = graph.is_sensible_graph(g)
            if warnings and not sensible:
                logging.warn("Ignoring sentence %s: %s" % (sent_id, explanation))
        if all((t.pstree != "_" for t in sentence)) and sensible:
            tree_src = []
            tree = None
            for token in sentence:
                tree_tok = token.word
                tree_tok = tree_tok.replace("(", "-LRB-")
                tree_tok = tree_tok.replace(")", "-RRB-")
                tree_pos = token.pos
                tree_pos = tree_pos.replace("(", "-LRB-")
                tree_pos = tree_pos.replace(")", "-RRB-")
                tree_frag = token.pstree
                tree_frag = tree_frag.replace("*", "(%s %s)" % (tree_pos, tree_tok))
                tree_src.append(tree_frag)
            tree_src = "".join(tree_src)
            try:
                tree = ParentedTree.fromstring(tree_src)
            except ValueError:
                logging.warn("Failed to construct parse tree from sentence %s: %s" % (sent_id, tree_src))
                tree = None
        if sensible and tree is not None:
            yield forms, tokens, g, tree


def _get_sentences(f):
    """A generator over the sentences in f."""
    sentence = []
    for line in f:
        line = line.strip()
        if line == "":
            yield sentence
            sentence = []
        else:
            fields = line.split("\t")
            sentence.append(TsvToken(*fields))
    if len(sentence) > 0:
        yield sentence
