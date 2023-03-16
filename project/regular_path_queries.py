from typing import List
from copy import copy

import numpy as np
import networkx as nx

from scipy.sparse import (
    coo_matrix,
    kron,
    find,
    csr_matrix,
    spmatrix,
    lil_matrix,
    vstack,
    identity,
)
from pyformlang.finite_automaton import EpsilonNFA, State

from project.finite_automatons import graph_to_nfa, regex_to_min_dfa


class BooleanDecomposition:
    """
    Boolean decomposition of the finite automata
    """

    def __init__(self, symbols_matrices: dict, states: list):
        """
        :param symbols_matrices: dict - edge symbol to its adjacency matrix
        :param states: states of the finite automata
        """
        self.symbols_matrices = symbols_matrices
        self.states = states

    def __str__(self):
        result = ""
        for (symbol, matrix) in self.to_dict().items():
            result += str(symbol) + "\n" + str(matrix.toarray()) + "\n"
        return result

    def states(self) -> list:
        return self.states

    def to_dict(self) -> dict:
        return self.symbols_matrices

    def __eq__(self, other):
        self_dict = self.to_dict()
        other_dict = other.to_dict()
        if not set(self.states) == set(other.states):
            return False
        if not set(self_dict.keys()) == set(other_dict.keys()):
            return False
        for i in self_dict.keys():
            nonzero_self = set(zip(*self_dict[i].nonzero()))
            nonzero2_other = set(zip(*other_dict[i].nonzero()))
            if not nonzero_self == nonzero2_other:
                return False
        return True

    def transitive_closure(self) -> coo_matrix:
        """
        Calculate transitive closure from symbols matrices
        :return: transitive closure adjacency matrix
        """
        adj_matrix = sum(
            self.to_dict().values(), coo_matrix((len(self.states), len(self.states)))
        )

        nnz_values = 0
        while nnz_values != adj_matrix.nnz:
            nnz_values = adj_matrix.nnz
            adj_matrix += adj_matrix @ adj_matrix

        return adj_matrix


class MatrixConcat:
    def __init__(self, lhs: spmatrix, rhs: spmatrix):
        self._lhs = lhs
        self._rhs = rhs

    def __copy__(self):
        return MatrixConcat(self._lhs.copy(), self._rhs.copy())

    def __eq__(self, other):
        if not isinstance(other, MatrixConcat):
            return False
        nnz_self = set(zip(*self._lhs.nonzero())).union(set(zip(*self._rhs.nonzero())))
        nnz_other = set(zip(*other._lhs.nonzero())).union(
            set(zip(*other._rhs.nonzero()))
        )
        return nnz_self == nnz_other

    def left_submatrix(self) -> spmatrix:
        return self._lhs

    def right_submatrix(self) -> spmatrix:
        return self._rhs

    def tocsr(self):
        _, width_left = self._lhs.get_shape()
        height_right, width_right = self._rhs.get_shape()
        data = [
            self._lhs.tocsr()[i, j] for (i, j) in zip(*self._lhs.tocsr().nonzero())
        ] + [self._rhs.tocsr()[i, j] for (i, j) in zip(*self._rhs.tocsr().nonzero())]
        row = [i for (i, _) in zip(*self._lhs.tocsr().nonzero())] + [
            i for (i, _) in zip(*self._rhs.tocsr().nonzero())
        ]
        col = [j for (_, j) in zip(*self._lhs.tocsr().nonzero())] + [
            width_left + j for (_, j) in zip(*self._rhs.tocsr().nonzero())
        ]
        return csr_matrix(
            (data, (row, col)), shape=(height_right, width_right + width_left)
        )

    def exclude_visited(self, other):
        for (i, j) in zip(*self._rhs.nonzero()):
            if other.right_submatrix()[i, j] != 0:
                self._rhs[i, j] = 0

    def merge(self, other, merge_factor: int):
        _, width_left = self._lhs.get_shape()
        _, width_right = self._rhs.get_shape()
        for (i, j) in zip(*other.left_submatrix().nonzero()):
            offset = i // merge_factor
            row = other.right_submatrix().getrow(i)
            for (_, k) in zip(*row.nonzero()):
                if row[0, k] != 0:
                    self._rhs[offset * merge_factor + j, k] = 1

    @classmethod
    def vstack(cls, lhs, rhs):
        return MatrixConcat(
            vstack((lhs.left_submatrix(), rhs.left_submatrix())).tolil(),
            vstack((lhs.right_submatrix(), rhs.right_submatrix())).tolil(),
        )


def spmatrix_to_matrix_concat(matrix: spmatrix, width_left: int) -> MatrixConcat:
    """
    Transform spmatrix to MatrixConcat
    :param matrix: spmatrix
    :param width_left: width of lhs in MatrixConcat
    :return: MatrixConcat
    """
    height, width = matrix.get_shape()
    matrix = matrix.tocsr()
    left_submatrix = lil_matrix((height, width_left))
    right_submatrix = lil_matrix((height, width - width_left))
    for (i, j) in zip(*matrix.nonzero()):
        if j < width_left:
            left_submatrix[i, j] = matrix[i, j]
        else:
            right_submatrix[i, j - width_left] = matrix[i, j]
    return MatrixConcat(left_submatrix, right_submatrix)


def enfa_to_boolean_decomposition(enfa: EpsilonNFA) -> BooleanDecomposition:
    """
    Returns boolean decomposition from given EpsilonNFA
    :param enfa: EpsilonNFA which will be decomposed
    :return: boolean decomposition of EpsilonNFA
    """
    enfa_states = list(enfa.states)
    boolean_decompose = dict()
    for (source, symbol_to_dest) in enfa.to_dict().items():
        for (symbol, dest) in symbol_to_dest.items():
            if symbol not in boolean_decompose:
                boolean_decompose[symbol] = list()
            try:
                iter(dest)
            except TypeError:
                boolean_decompose[symbol].append(
                    (enfa_states.index(source), enfa_states.index(dest))
                )
            else:
                for d in dest:
                    boolean_decompose[symbol].append(
                        (enfa_states.index(source), enfa_states.index(d))
                    )

    coo_matrices = dict()
    for (symbol, edges) in boolean_decompose.items():
        row = np.array([i for (i, _) in edges])
        col = np.array([j for (_, j) in edges])
        data = np.array([1 for _ in range(len(edges))])
        coo_matrices[symbol] = coo_matrix(
            (data, (row, col)), shape=(len(enfa.states), len(enfa.states))
        )

    return BooleanDecomposition(coo_matrices, enfa_states)


def direct_sum(
    lhs: BooleanDecomposition, rhs: BooleanDecomposition
) -> BooleanDecomposition:
    """
    Calculate direct sum of two boolean decompositions
    """
    result = dict()
    symbols = set(lhs.to_dict().keys()).union(set(rhs.to_dict().keys()))
    for symbol in symbols:
        if symbol in lhs.to_dict():
            coo_matrix1 = lhs.to_dict()[symbol].tocsr()
        else:
            coo_matrix1 = csr_matrix((len(lhs.states), len(lhs.states)))

        if symbol in rhs.to_dict():
            coo_matrix2 = rhs.to_dict()[symbol].tocsr()
        else:
            coo_matrix2 = csr_matrix((len(rhs.states), len(rhs.states)))

        result[symbol] = coo_matrix(
            (len(lhs.states) + len(rhs.states), len(lhs.states) + len(rhs.states))
        )
        data = [coo_matrix1[i, j] for (i, j) in zip(*coo_matrix1.nonzero())] + [
            coo_matrix2[i, j] for (i, j) in zip(*coo_matrix2.nonzero())
        ]
        row = [i for (i, _) in zip(*coo_matrix1.nonzero())] + [
            len(lhs.states) + i for (i, _) in zip(*coo_matrix2.nonzero())
        ]
        col = [j for (_, j) in zip(*coo_matrix1.nonzero())] + [
            len(lhs.states) + j for (_, j) in zip(*coo_matrix2.nonzero())
        ]
        shape_width = len(lhs.states) + len(rhs.states)
        result[symbol] = coo_matrix(
            (data, (row, col)), shape=(shape_width, shape_width)
        )

    return BooleanDecomposition(result, lhs.states + rhs.states)


def kron_boolean_decomposition(
    lhs: BooleanDecomposition, rhs: BooleanDecomposition
) -> BooleanDecomposition:
    """
    Calculate kronecker prod between two matrices` boolean decompositions. Matrices must have same symbols
    :param lhs: left argument of kron prod
    :param rhs: right argument of kron prod
    :return: boolean decomposition of kron prod
    """
    intersect_dcmps = dict()
    for symbol in set(lhs.to_dict().keys()).union(set(rhs.to_dict().keys())):
        if symbol in lhs.to_dict():
            coo_matrix1 = lhs.to_dict()[symbol]
        else:
            coo_matrix1 = coo_matrix((len(lhs.states), (len(lhs.states))))

        if symbol in rhs.to_dict():
            coo_matrix2 = rhs.to_dict()[symbol]
        else:
            coo_matrix2 = coo_matrix((len(rhs.states), len(rhs.states)))

        intersect_dcmps[symbol] = kron(coo_matrix1, coo_matrix2)

    intersect_states = list()
    for s_lhs in lhs.states:
        for s_rhs in rhs.states:
            intersect_states.append(State((s_lhs, s_rhs)))

    return BooleanDecomposition(intersect_dcmps, intersect_states)


def intersect_enfa(enfa_lhs: EpsilonNFA, enfa_rhs: EpsilonNFA) -> EpsilonNFA:
    """
    Calculate an intersection of two EpsilonNFAs
    :param enfa_lhs: left argument of intersection operation
    :param enfa_rhs: right argument of intersection operation
    :return: result of the intersection operation
    """
    dcmps_lhs = enfa_to_boolean_decomposition(enfa_lhs)
    dcmps_rhs = enfa_to_boolean_decomposition(enfa_rhs)
    intersect_dcmps = kron_boolean_decomposition(dcmps_lhs, dcmps_rhs)

    start_states = list()
    for s_lhs in enfa_lhs.start_states:
        for s_rhs in enfa_rhs.start_states:
            start_states.append(State((s_lhs, s_rhs)))

    final_states = list()
    for s_lhs in enfa_lhs.final_states:
        for s_rhs in enfa_rhs.final_states:
            final_states.append(State((s_lhs, s_rhs)))

    result = EpsilonNFA()
    intersect_states = intersect_dcmps.states
    for (symbol, matrix) in intersect_dcmps.to_dict().items():
        (rows, cols, _) = find(matrix)
        for i in range(len(cols)):
            result.add_transition(
                intersect_states[rows[i]], symbol, intersect_states[cols[i]]
            )

    for start_state in start_states:
        result.add_start_state(start_state)

    for final_state in final_states:
        result.add_final_state(final_state)

    return result


def regular_path_query(
    regex_str: str,
    graph: nx.MultiDiGraph,
    start_states: set = None,
    final_states: set = None,
) -> set:
    """
    Perform a rpq in a given graph with regex
    :param regex_str: string containing regex
    :param graph: graph to run rpq on
    :param start_states: start states of rpq in a given graph
    :param final_states: final states of rpq in a given graph
    :return: set of tuples which satisfies given rpq. First elements are start states and second are final states
    """
    if start_states is None:
        start_states = list(graph.nodes)

    if final_states is None:
        final_states = list(graph.nodes)

    enfa_graph = graph_to_nfa(graph, start_states, final_states)
    enfa_regex = regex_to_min_dfa(regex_str)
    intersection = intersect_enfa(enfa_graph, enfa_regex)
    bd_intersection = enfa_to_boolean_decomposition(intersection)
    results = set()
    for (i, j) in zip(*bd_intersection.transitive_closure().nonzero()):
        (graph_start_state, regex_start_state) = bd_intersection.states[i].value
        (graph_final_state, regex_final_state) = bd_intersection.states[j].value
        if (
            graph_start_state in start_states
            and graph_final_state in final_states
            and regex_start_state in enfa_regex.start_states
            and regex_final_state in enfa_regex.final_states
        ):
            results.add((graph_start_state, graph_final_state))

    return results


def bfs_regular_path_query(
    regex: str,
    graph: nx.MultiDiGraph,
    separate: bool,
    start_states: List[any] = None,
    final_states: List[any] = None,
):
    """
    Performs bfs on graph with given regex
    :param regex: regex on a given graph
    :param graph: graph where to perform bfs
    :param separate: defines the type of return value
    :param start_states: start nodes of the given graph
    :param final_states: final nodes of the given graph
    :return: if separate == True -> set of 2-element tuples of connected graph nodes
                       otherwise -> set of graph nodes, accessible from start_states
    """
    dcmps = enfa_to_boolean_decomposition(graph_to_nfa(graph))
    regex_as_enfa = regex_to_min_dfa(regex)
    regex_dcmps = enfa_to_boolean_decomposition(regex_as_enfa)
    direct_sum_dcmps = direct_sum(regex_dcmps, dcmps)

    if not separate:
        visited = MatrixConcat(
            identity(len(regex_dcmps.states)),
            lil_matrix((len(regex_dcmps.states), len(dcmps.states))),
        )
        frontier = copy(visited)
        for state in start_states:
            frontier.right_submatrix()[
                regex_dcmps.states.index(regex_as_enfa.start_state),
                dcmps.states.index(state),
            ] = 1
    else:
        visited = MatrixConcat(
            identity(len(regex_dcmps.states)),
            lil_matrix((len(regex_dcmps.states), len(dcmps.states))),
        )
        for _ in range(len(start_states) - 1):
            visited = MatrixConcat.vstack(
                visited,
                MatrixConcat(
                    identity(len(regex_dcmps.states)),
                    lil_matrix((len(regex_dcmps.states), len(dcmps.states))),
                ),
            )
        frontier = copy(visited)
        for i in range(len(start_states)):
            state = start_states[i]
            frontier.right_submatrix()[
                regex_dcmps.states.index(regex_as_enfa.start_state)
                + i * len(regex_dcmps.states),
                dcmps.states.index(state),
            ] = 1

    while True:
        last_iteration_visited = copy(visited)
        frontier.exclude_visited(visited)
        new_frontier = copy(frontier)
        for matrix in direct_sum_dcmps.to_dict().values():
            next_step = spmatrix_to_matrix_concat(
                frontier.tocsr() @ matrix.tocsr(), len(regex_dcmps.states)
            )
            new_frontier.merge(next_step, len(regex_dcmps.states))
        visited.merge(frontier, len(regex_dcmps.states))
        frontier = new_frontier

        if last_iteration_visited.tocsr().nnz == visited.tocsr().nnz:
            break

    result = set()
    if not separate:
        for final_regex in regex_as_enfa.final_states:
            row = visited.right_submatrix().getrow(
                regex_dcmps.states.index(final_regex)
            )
            for (_, j) in zip(*row.nonzero()):
                state = dcmps.states[j].value
                if state not in start_states and (
                    final_states is None or state in final_states
                ):
                    result.add(state)
    else:
        for i in range(len(start_states)):
            inter_result = set()
            for final_regex in regex_as_enfa.final_states:
                offset = i * len(regex_dcmps.states)
                row = visited.right_submatrix().getrow(
                    offset + regex_dcmps.states.index(final_regex)
                )
                for (_, j) in zip(*row.nonzero()):
                    state = dcmps.states[j].value
                    if state not in start_states and (
                        final_states is None or state in final_states
                    ):
                        inter_result.add((start_states[i], state))
            result = result.union(inter_result)

    return result
