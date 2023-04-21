import collections
from enum import Enum
from typing import Set, Tuple, List

import numpy as np
import cfpq_data
from scipy.sparse import dok_matrix
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


def matrix_transitive_closure(
    graph: MultiDiGraph, cfg: CFG
) -> set[tuple[any, Variable, any]]:
    """
    Solves reachability problem in the given graph with given context free grammar, i.e. find closure
    :param graph: graph where matrix algorithm will be performed
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

    boolean_dcmps_res = dict()
    boolean_dcmps_dok_res = dict()

    nodes = list(graph.nodes)
    graph_size = len(nodes)

    for var in cfg.variables:
        boolean_dcmps_dok_res[var] = dok_matrix(
            (graph_size, graph_size), dtype=np.int32
        )

    for v, u, d in graph.edges(data=True):
        label = d["label"]
        v = nodes.index(v)
        u = nodes.index(u)
        if label in term_to_var:
            for var in term_to_var[label]:
                boolean_dcmps_dok_res[var][v, u] = 1

    for v in graph.nodes:
        v = nodes.index(v)
        for var in eps_vars:
            boolean_dcmps_dok_res[var][v, v] = 1

    for k, v in boolean_dcmps_dok_res.items():
        boolean_dcmps_res[k] = v.tocsr()

    do_iter = True
    while do_iter:
        last_nnz = sum([m.getnnz() for m in boolean_dcmps_res.values()])

        for (var1, var2), variables in pair_vars_to_var.items():
            for var in variables:
                boolean_dcmps_res[var] += (
                    boolean_dcmps_res[var1] @ boolean_dcmps_res[var2]
                )

        do_iter = last_nnz != sum([m.getnnz() for m in boolean_dcmps_res.values()])

    for var, mat in boolean_dcmps_res.items():
        rows, cols = mat.nonzero()
        for i in range(len(rows)):
            result.add((nodes[rows[i]], var, nodes[cols[i]]))

    return result


class CfpqClosureType(Enum):
    HELLINGS = hellings_transitive_closure
    MATRIX = matrix_transitive_closure


def context_free_path_query(
    cfg: CFG,
    graph: MultiDiGraph,
    start_var: Variable = Variable("S"),
    start_nodes: List[any] = None,
    final_nodes: List[any] = None,
    closure_type: CfpqClosureType = CfpqClosureType.HELLINGS,
) -> Set[Tuple[any, any]]:
    """
    Performs context free path query in the graph with given context free grammar

    :param cfg: context free grammar
    :param graph: graph to inspect
    :param start_var: start nonterminal symbol
    :param start_nodes: start nodes inside graph (all nodes if None)
    :param final_nodes: final nodes inside graph (all nodes if None)
    :param closure_type: algorithm used to find transitive closure
    :return: 2 element tuples with nodes satisfying cfpq
    """
    if start_nodes is None:
        start_nodes = list(graph.nodes)

    if final_nodes is None:
        final_nodes = list(graph.nodes)

    closure = closure_type(graph, cfg)
    return set(
        [
            (u, v)
            for u, var, v in closure
            if var == start_var and u in start_nodes and v in final_nodes
        ]
    )
