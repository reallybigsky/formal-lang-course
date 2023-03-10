from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import DeterministicFiniteAutomaton, EpsilonNFA
import networkx as nx


def get_min_dfa_from_regex(expr: str) -> DeterministicFiniteAutomaton:
    """
    Builds minimal Deterministic Finite Automaton (DFA) from given regular expression

    :param expr: regular expression
    :return: minimal Deterministic Finite Automaton (DFA)
    """
    regex = Regex(expr)
    return regex.to_epsilon_nfa().minimize()


def get_nfa_from_graph(
    graph: nx.MultiDiGraph, start_nodes: set = None, final_nodes: set = None
) -> EpsilonNFA:
    """
    Builds Nondeterministic Finite Automaton from directed graph

    :param graph: directed graph which is used as a frame of returned NFA
    :param start_nodes: set of start states nodes
    :param final_nodes: set of final state nodes
    :return: NFA
    """
    nfa = EpsilonNFA()
    if final_nodes is None:
        final_nodes = set(graph.nodes)
    if start_nodes is None:
        start_nodes = set(graph.nodes)

    for node in start_nodes:
        nfa.add_start_state(node)
    for node in final_nodes:
        nfa.add_final_state(node)

    for v, u, data in graph.edges(data=True):
        nfa.add_transition(v, data["label"], u)
    return nfa
