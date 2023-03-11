import numpy as np
import networkx as nx

from scipy.sparse import coo_matrix, kron, find
from pyformlang.finite_automaton import EpsilonNFA, State

from project.finite_automatons import get_nfa_from_graph, get_min_dfa_from_regex


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


def boolean_decomposition_from_enfa(enfa: EpsilonNFA) -> BooleanDecomposition:
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


def kron_boolean_decomposition(
    dcmps_lhs: BooleanDecomposition, dcmps_rhs: BooleanDecomposition
) -> BooleanDecomposition:
    """
    Calculate kronecker prod between two matrices` boolean decompositions. Matrices must have same symbols
    :param dcmps_lhs: left argument of kron prod
    :param dcmps_rhs: right argument of kron prod
    :return: boolean decomposition of kron prod
    """
    intersect_dcmps = dict()
    d_lhs = dcmps_lhs.to_dict()
    d_rhs = dcmps_rhs.to_dict()
    for symbol in set(d_lhs.keys()).union(set(d_rhs.keys())):
        if symbol in d_lhs:
            coo_matrix1 = d_lhs[symbol]
        else:
            coo_matrix1 = coo_matrix((len(dcmps_lhs.states), (len(dcmps_lhs.states))))

        if symbol in d_rhs:
            coo_matrix2 = d_rhs[symbol]
        else:
            coo_matrix2 = coo_matrix((len(dcmps_rhs.states), len(dcmps_rhs.states)))

        intersect_dcmps[symbol] = kron(coo_matrix1, coo_matrix2)

    intersect_states = list()
    for s_lhs in dcmps_lhs.states:
        for s_rhs in dcmps_rhs.states:
            intersect_states.append(State((s_lhs, s_rhs)))

    return BooleanDecomposition(intersect_dcmps, intersect_states)


def intersect_enfa(enfa_lhs: EpsilonNFA, enfa_rhs: EpsilonNFA) -> EpsilonNFA:
    """
    Calculate an intersection of two EpsilonNFAs
    :param enfa_lhs: left argument of intersection operation
    :param enfa_rhs: right argument of intersection operation
    :return: result of the intersection operation
    """
    dcmps_lhs = boolean_decomposition_from_enfa(enfa_lhs)
    dcmps_rhs = boolean_decomposition_from_enfa(enfa_rhs)
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

    enfa_graph = get_nfa_from_graph(graph, start_states, final_states)
    enfa_regex = get_min_dfa_from_regex(regex_str)
    intersection = intersect_enfa(enfa_graph, enfa_regex)
    bd_intersection = boolean_decomposition_from_enfa(intersection)
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
