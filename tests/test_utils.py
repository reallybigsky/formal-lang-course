import io
import pydot

from typing import List
from pyformlang.finite_automaton import EpsilonNFA
from networkx import MultiDiGraph
from project.language.interpreter import interpret


def interpret_to_str(*args, **kwargs):
    with io.StringIO() as output:
        kwargs["out"] = output
        interpret(*args, **kwargs)
        return output.getvalue()


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


def deep_compare(a_graph: pydot.Dot, b_graph: pydot.Dot) -> bool:
    start_a = a_graph.get_node("1")
    start_b = b_graph.get_node("1")

    edges_a = a_graph.get_edge_list()
    edges_b = b_graph.get_edge_list()

    if len(start_a) != len(start_b) or len(start_a) != 1:
        return False

    query = [(start_a[0], start_b[0])]

    def strip_label(lab: str):
        return lab.strip('"')

    def get_neighbors(edges: List[pydot.Edge]) -> List[pydot.Node] | bool:
        result = []
        for edge in filter(lambda e: e.get_source() == a.get_name(), edges):
            nodes = a_graph.get_node(edge.get_destination())
            if len(nodes) != 1:
                return False
            result.append(nodes[0])
        return result

    while len(query) > 0:
        a, b = query.pop()
        if strip_label(a.get("label")) != strip_label(b.get("label")):
            return False

        neighbours_a = get_neighbors(edges_a)
        neighbours_b = get_neighbors(edges_b)

        if len(neighbours_a) != len(neighbours_b):
            return False

        for p in zip(neighbours_a, neighbours_b):
            query.append(p)

    return True


def dot_from_string(s: str) -> pydot.Dot:
    graphs = pydot.graph_from_dot_data(s)
    return graphs[0]
