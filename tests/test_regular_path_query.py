import numpy as np

from typing import List
from scipy.sparse import coo_matrix

from pyformlang.finite_automaton import State, Symbol

from tests.test_utils import create_automata, create_graph
from project.regular_path_queries import intersect_enfa, regular_path_query
from project.regular_path_queries import kron_boolean_decomposition as kron_bd, BooleanDecomposition as bd


def test_kron_boolean_decomposition():
    bd_res = kron_bd(
        bd({Symbol("a"): coo_matrix((np.array([1]), (np.array([0]), np.array([0]))), shape=(1, 1))}, [State(0)], ),
        bd({Symbol("a"): coo_matrix((np.array([1]), (np.array([0]), np.array([0]))), shape=(1, 1))}, [State(0)], ),
    )
    bd_exp = bd({Symbol("a"): coo_matrix((np.array([1]), (np.array([0]), np.array([0]))), shape=(1, 1))},
                [State((State(0), State(0)))],
                )
    assert bd_res == bd_exp

    bd_res = kron_bd(
        bd({Symbol("a"): coo_matrix((np.array([1]), (np.array([0]), np.array([0]))), shape=(1, 1))}, [State(0)], ),
        bd({Symbol("b"): coo_matrix((np.array([1]), (np.array([0]), np.array([0]))), shape=(1, 1))}, [State(0)], ),
    )
    bd_exp = bd({Symbol("a"): coo_matrix((1, 1)), Symbol("b"): coo_matrix((1, 1))},
                [State((State(0), State(0)))],
                )

    assert bd_res == bd_exp


def test_intersect_enfa():
    def helper_test_intersect_enfa(tr_lhs: List[tuple], ss_lhs: List, fs_lhs: List,
                                   tr_rhs: List[tuple], ss_rhs: List, fs_rhs: List,
                                   tr_exp: List[tuple], ss_exp: List, fs_exp: List):
        nfa_lhs = create_automata(tr_lhs, ss_lhs, fs_lhs)
        nfa_rhs = create_automata(tr_rhs, ss_rhs, fs_rhs)
        nfa_exp = create_automata(tr_exp, ss_exp, fs_exp)
        nfa_res = intersect_enfa(nfa_lhs, nfa_rhs)
        assert nfa_exp == nfa_res

    helper_test_intersect_enfa([(0, "a", 0)], [0], [0],
                               [(0, "a", 0)], [0], [0],
                               [(0, "a", 0)], [0], [0])

    helper_test_intersect_enfa([(0, "a", 0)], [0], [0],
                               [(0, "b", 0)], [0], [0],
                               [], [0], [0])

    helper_test_intersect_enfa([(0, "a", 0)], [0], [0],
                               [(0, "a", 1), (1, "b", 2)], [0], [1, 2],
                               [(0, "a", 1)], [0], [1])

    helper_test_intersect_enfa([(0, "a", 1), (0, "b", 2)], [0], [1, 2],
                               [(0, "a", 1), (0, "b", 2), (1, "a", 1), (2, "b", 2)], [0], [1, 2],
                               [(0, "a", 1), (0, "b", 2)], [0], [1, 2])


def test_regular_path_query():
    assert regular_path_query("a*",
                              create_graph(nodes=[0, 1], edges=[(0, "a", 1)])
                              ) == {(State(0), State(1))}

    assert regular_path_query("a.b",
                              create_graph(nodes=[0, 1, 2], edges=[(0, "a", 1), (1, "b", 2)])
                              ) == {(State(0), State(2))}

    assert regular_path_query("a*",
                              create_graph(nodes=[0, 1, 2], edges=[(0, "a", 1), (1, "a", 2)])
                              ) == {(State(0), State(1)), (State(1), State(2)), (State(0), State(2))}

    assert regular_path_query("(a.b)|c",
                              create_graph(nodes=[0, 1, 2], edges=[(0, "c", 0), (0, "a", 1), (1, "b", 2)])
                              ) == {(State(0), State(2)), (State(0), State(0))}

    assert regular_path_query("c*.a.b",
                              create_graph(nodes=[0, 1, 2], edges=[(0, "c", 0), (0, "a", 1), (1, "b", 2)])
                              ) == {(State(0), State(2))}
