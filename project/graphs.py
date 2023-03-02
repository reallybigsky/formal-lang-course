import cfpq_data as cfpq
import networkx as nx


class GraphInfo:
    def __init__(self, nodes, edges, labels):
        self.nodes = nodes
        self.edges = edges
        self.labels = labels

    def __eq__(self, other):
        return (
            self.nodes == other.nodes
            and self.edges == other.edges
            and self.labels == other.labels
        )

    def labels_to_list(self):
        return list([label for _, _, label in self.labels])


def get_nx_graph_by_name(name: str) -> nx.MultiDiGraph:
    graph_path = cfpq.download(name)
    graph = cfpq.graph_from_csv(graph_path)
    return graph


def get_graph_info_by_name(name: str) -> GraphInfo:
    graph = get_nx_graph_by_name(name)
    return GraphInfo(
        graph.number_of_nodes(), graph.number_of_edges(), graph.edges(data="label")
    )


def create_two_cycles_graph(n: int, m: int, labels) -> nx.MultiDiGraph:
    return cfpq.labeled_two_cycles_graph(n, m, labels=labels)


def save_graph_as_pydot(graph: nx.MultiDiGraph, path: str):
    pydot_graph = nx.nx_pydot.to_pydot(graph)
    pydot_graph.write_raw(path)


def create_and_save_two_cycles_graph_as_pydot(n: int, m: int, labels, path: str):
    graph = cfpq.labeled_two_cycles_graph(n, m, labels=labels)
    save_graph_as_pydot(graph, path)
