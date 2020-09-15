#!/usr/bin/env python3

import networkx


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
