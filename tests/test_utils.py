from typing import List
from pyformlang.finite_automaton import EpsilonNFA
from networkx import MultiDiGraph


def create_automata(
    transitions: List[tuple], start_states: List, final_states: List
) -> EpsilonNFA:
    automaton = EpsilonNFA()
    automaton.add_transitions(transitions)
    for ss in start_states:
        automaton.add_start_state(ss)
    for fs in final_states:
        automaton.add_final_state(fs)

    return automaton


def create_graph(nodes: list, edges: list) -> MultiDiGraph:
    graph = MultiDiGraph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(
        list(map(lambda edge: (edge[0], edge[2], {"label": edge[1]}), edges))
    )
    return graph
