#!/usr/bin/env python3

import collections
import logging
import re

import networkx

from textcomplexity.utils import graph

UdToken = collections.namedtuple("UdToken", "id form lemma upos xpos feats head deprel deps misc".split())
Token = collections.namedtuple("Token", "word pos upos".split())


def read_conllu_sentences(f, *, warnings=True):
    for sentence, sent_id in _read_conllu(f):
        tokens = _get_tokens(sentence)
        tokens = [Token(t.form, t.xpos, t.upos) for t in tokens]
        g = _create_nx_digraph(sentence, sent_id)
        sensible, explanation = graph.is_sensible_graph(g)
        if sensible:
            yield tokens, g
        else:
            if warnings:
                logging.warn("Ignoring sentence with ID %s: %s" % (sent_id, explanation))


def _get_tokens(sentence):
    id_range = re.compile(r"^(?P<start>\d+)-(?P<end>\d+)$")
    simple_id = re.compile(r"^\d+$")
    output = []
    current_mwu = 0
    for token in sentence:
        m_range = id_range.search(token.id)
        m_simple = simple_id.search(token.id)
        if m_range:
            cstart = int(m_range.group("start"))
            cend = int(m_range.group("end"))
            current_mwu = int(cend)
            output.append(token)
        elif m_simple:
            if int(token.id) > current_mwu:
                output.append(token)
    return output


def _read_conllu(f):
    pattern = re.compile(r"^#\s*sent_id\s*=\s*(\S.*)$")
    sentence = []
    origid = ""
    for line in f:
        if line.startswith("#"):
            m = re.search(pattern, line)
            if m:
                origid = m.group(1)
            continue
        line = line.strip()
        if line == "":
            yield sentence, origid
            sentence = []
            origid = ""
        else:
            fields = line.split("\t")
            sentence.append(UdToken(*fields))
    if len(sentence) > 0:
        yield sentence, origid


def _create_nx_digraph(sentence, origid=None):
    """Return a networkx.DiGraph object of the CoNLL-U representation."""
    def attributes(t):
        return {"word": t.form, "lemma": t.lemma, "wc": t.upos, "pos": t.xpos}

    dg = networkx.DiGraph()
    if origid is not None:
        dg.graph["origid"] = origid
    dg.add_nodes_from([(i, attributes(t)) for i, t in enumerate(sentence)])
    id_to_enumeration = {t.id: i for i, t in enumerate(sentence)}
    for i, token in enumerate(sentence):
        if token.deprel == "root":
            dg.nodes[i]["root"] = "root"
    for i, token in enumerate(sentence):
        relations = set()
        if token.deps != "_":
            for rel in token.deps.split("|"):
                gov, relation = rel.split(":", maxsplit=1)
                if relation != "root":
                    governor = id_to_enumeration[gov]
                    relations.add((governor, relation))
        elif token.deprel != "_":
            if token.deprel != "root":
                relations.add((id_to_enumeration[token.head], token.deprel))
        for governor, relation in relations:
            # if relation == "punct":
            #     continue
            dg.add_edge(governor, i, relation=relation)
    # remove unconnected vertices, e.g. range tokens
    for v, l in list(dg.nodes(data=True)):
        if "root" not in l and dg.degree[v] == 0:
            dg.remove_node(v)
    return dg
