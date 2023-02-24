import cfpq_data as cfpq
import networkx


class Graph:
    def __init__(self, nodes, edges, labels):
        self.nodes = nodes
        self.edges = edges
        self.labels = labels

    def __eq__(self, other):
        return self.nodes == other.nodes and self.edges == other.edges and self.labels == other.labels

    def labels_to_list(self):
        return list([label for _, _, label in self.labels])


def get_graph(name: str) -> Graph:
    graph_path = cfpq.download(name)
    graph = cfpq.graph_from_csv(graph_path)
    return Graph(graph.number_of_nodes(), graph.number_of_edges(), graph.edges(data="label"))


def create_two_cycles_graph(n: int, m: int, labels) -> networkx.MultiDiGraph:
    return cfpq.labeled_two_cycles_graph(n, m, labels=labels)


def save_graph_as_pydot(graph: networkx.MultiDiGraph, path: str):
    pydot_graph = networkx.nx_pydot.to_pydot(graph)
    pydot_graph.write_raw(path)
