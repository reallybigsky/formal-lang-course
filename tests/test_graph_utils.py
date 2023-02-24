import filecmp
import os
from project import graph_utils


def test_get_graph():
    graph_pr = graph_utils.get_graph("pr")
    assert graph_pr.nodes == 815
    assert graph_pr.edges == 692
    assert set(graph_pr.labels_to_list()) == {"a", "d"}

    graph_pr = graph_utils.get_graph("ls")
    assert graph_pr.nodes == 1687
    assert graph_pr.edges == 1453
    assert set(graph_pr.labels_to_list()) == {"a", "d"}


def test_create_and_save_two_cycles_graph():
    graph = graph_utils.create_two_cycles_graph(42, 29, labels=("a", "d"))
    graph_utils.save_graph_as_pydot(graph, "tmp_two_cycles_graph_42_29")
    assert filecmp.cmp("./tmp_two_cycles_graph_42_29", "./test_graph_utils_two_cycles_graph_42_29_expected")
    os.remove("./tmp_two_cycles_graph_42_29")
