import collections
from typing import Set, Tuple, List

import cfpq_data
from pyformlang.cfg import CFG, Terminal, Variable
from networkx import MultiDiGraph


def import_cfg_from_text(text: str) -> CFG:
    """
    Load context free grammar from text
    :param text
    :return: CFG from text
    """
    return cfpq_data.cfg_from_text(text)


def import_cfg_from_txt(path: str) -> CFG:
    """
    Load context free grammar from file
    :param path: filepath with CFG
    :return: CFG from file
    """
    return cfpq_data.cfg_from_txt(path)


def cfg_to_weak_cnf(cfg: CFG) -> CFG:
    """
    Convert context free grammar to weak Chomsky normal form
    :param cfg: context free grammar
    :return: weak Chomsky normal form
    """
    cfg_no_unit_prods = cfg.eliminate_unit_productions().remove_useless_symbols()
    new_prods = cfg_no_unit_prods._get_productions_with_only_single_terminals()
    new_prods = cfg_no_unit_prods._decompose_productions(new_prods)
    result = CFG(
        start_symbol=cfg_no_unit_prods.start_symbol,
        productions=set(new_prods),
    )
    return result


def hellings_transitive_closure(
    graph: MultiDiGraph, cfg: CFG
) -> Set[Tuple[any, Variable, any]]:
    """
    Solves reachability problem in the given graph with given context free grammar, i.e. find closure
    :param graph: graph where Hellings algorithm will be performed
    :param cfg: context free grammar
    :return: Set of 3 element tuples (vertex, nonterminal, vertex)
    """

    cfg = cfg_to_weak_cnf(cfg)

    result = set()
    eps_vars = set()
    term_to_var = dict()
    pair_vars_to_var = dict()

    for production in cfg.productions:
        match production.body:
            case []:
                eps_vars.add(production.head)
            case [Terminal() as term]:
                if term not in term_to_var:
                    term_to_var[term.value] = set()
                term_to_var[term.value].add(production.head)
            case [Variable() as var1, Variable() as var2]:
                if (var1, var2) not in pair_vars_to_var:
                    pair_vars_to_var[(var1, var2)] = set()
                pair_vars_to_var[(var1, var2)].add(production.head)

    for v, u, d in graph.edges(data=True):
        label = d["label"]
        if label in term_to_var:
            for var in term_to_var[label]:
                result.add((v, var, u))

    for node in graph.nodes:
        for var in eps_vars:
            result.add((node, var, node))

    queue = collections.deque(result)

    while len(queue) > 0:
        tmpres = set()
        v, var1, u = queue.popleft()
        for triple in result:
            if triple[2] != v:
                continue
            var0 = triple[1]
            start = triple[0]
            if (var0, var1) not in pair_vars_to_var:
                continue
            for var in pair_vars_to_var[(var0, var1)]:
                if (start, var, u) in result:
                    continue
                queue.append((start, var, u))
                tmpres.add((start, var, u))
        for triple in result:
            if triple[0] != u:
                continue
            var2 = triple[1]
            end = triple[2]
            if (var1, var2) not in pair_vars_to_var:
                continue
            for var in pair_vars_to_var[(var1, var2)]:
                if (v, var, end) in result:
                    continue
                queue.append((v, var, end))
                tmpres.add((v, var, end))
        result = result.union(tmpres)

    return result


def context_free_path_query(
    cfg: CFG,
    graph: MultiDiGraph,
    start_var: Variable = Variable("S"),
    start_nodes: List[any] = None,
    final_nodes: List[any] = None,
) -> Set[Tuple[any, any]]:
    """
    Performs context free path query in the graph with given context free grammar

    :param cfg: context free grammar
    :param graph: graph to inspect
    :param start_var: start nonterminal symbol
    :param start_nodes: start nodes inside graph (all nodes if None)
    :param final_nodes: final nodes inside graph (all nodes if None)
    :return: 2 element tuples with nodes satisfying cfpq
    """
    if start_nodes is None:
        start_nodes = list(graph.nodes)

    if final_nodes is None:
        final_nodes = list(graph.nodes)

    hell = hellings_transitive_closure(graph, cfg)
    return set(
        [
            (u, v)
            for u, var, v in hell
            if var == start_var and u in start_nodes and v in final_nodes
        ]
    )
